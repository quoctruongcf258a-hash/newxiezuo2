import os, json, subprocess, psutil
import paths  # 所有路径从 paths.py 导入，本模块不再自己拼绝对路径

CFG = os.path.join(paths.RULES_DIR, "ai_apps.json")
EDGE_CDP_DIR = paths.join("edge_cdp")  # 浏览器 CDP 用户数据目录（跟程序走）

# 让子进程脱离父进程（Windows）
DETACHED = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

# 记录本程序启动的进程 PID，便于「关闭」时精确关闭对应实例（不误伤其它浏览器窗口）
_launched_pids = {}


def _browser_install_paths():
    """返回已知浏览器可执行文件的候选路径（按通用安装位置推导，不写死盘符）。"""
    envs = [os.environ.get(e) for e in ("ProgramFiles", "ProgramFiles(x86)")]
    envs = [e for e in envs if e]
    local = os.environ.get("LOCALAPPDATA")
    # 各浏览器的系统级安装子路径
    cands = {
        "msedge": ["Microsoft\\Edge\\Application\\msedge.exe"],
        "chrome": ["Google\\Chrome\\Application\\chrome.exe"],
        "chromium": ["Chromium\\Application\\chromium.exe"],
        "brave": ["BraveSoftware\\Brave-Browser\\Application\\brave.exe"],
        "opera": ["Opera\\launcher.exe", "Opera\\opera.exe"],
        "firefox": ["Mozilla Firefox\\firefox.exe"],
        "vivaldi": ["Vivaldi\\Application\\vivaldi.exe"],
    }
    # 用户级安装（如 Chrome/Edge 装在当前用户目录）
    user_cands = {
        "chrome": [os.path.join("Google", "Chrome", "Application", "chrome.exe")],
        "chromium": [os.path.join("Chromium", "Application", "chromium.exe")],
        "msedge": [os.path.join("Microsoft", "Edge", "Application", "msedge.exe")],
        "brave": [os.path.join("BraveSoftware", "Brave-Browser", "Application", "brave.exe")],
    }
    out = {}
    for k, subs in cands.items():
        found = []
        for base in envs:
            for sub in subs:
                p = os.path.join(base, sub)
                if os.path.exists(p):
                    found.append(p)
        if k in user_cands and local:
            for sub in user_cands[k]:
                p = os.path.join(local, sub)
                if os.path.exists(p):
                    found.append(p)
        if found:
            out[k] = found
    return out


def _reg_app_path(exe_name):
    """从 Windows『App Paths』注册表查询 exe 完整路径（兼容 64/32 位视图）。"""
    try:
        import winreg
    except Exception:
        return None
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\\" + exe_name
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(root, key_path,
                               access=winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as k:
                val, _ = winreg.QueryValueEx(k, "")
                if val and os.path.exists(val):
                    return val
        except OSError:
            continue
    return None


def _find_browser(name):
    """按配置名查找浏览器可执行文件；找不到再回退其它已安装浏览器。"""
    name = (name or "msedge").lower().replace(".exe", "")
    if os.path.isabs(name) and os.path.exists(name):
        return name
    paths = _browser_install_paths()
    if name in paths:
        return paths[name][0]
    reg = _reg_app_path(name + ".exe")
    if reg:
        return reg
    # 回退：任意一个已安装浏览器（优先支持 CDP 的）
    for k in ("msedge", "chrome", "chromium", "brave", "vivaldi", "opera", "firefox"):
        if k in paths:
            return paths[k][0]
        r = _reg_app_path(k + ".exe")
        if r:
            return r
    return None


def load_players():
    with open(CFG, encoding="utf-8") as f:
        return json.load(f)


def save_players(ps):
    json.dump(ps, open(CFG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def is_running(p):
    n = p.get("进程名") or ""
    if not n: return False
    for x in psutil.process_iter(['name']):
        if (x.info['name'] or "").lower().startswith(n.lower()):
            return True
    return False


def cdp_alive(port):
    if not port: return False
    import socket
    s = socket.socket()
    s.settimeout(0.2)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except:
        return False
    finally:
        s.close()


def launch(p):
    t = p.get("类型")
    port = p.get("cdp_port")
    if t == "electron":
        exe = p.get("exe")
        if not exe or not os.path.exists(exe):
            return f"exe 不存在: {exe}"
        args = [exe]
        if port:
            args += [f"--remote-debugging-port={port}", "--remote-allow-origins=*"]
        # 关键：脱离父进程
        proc = subprocess.Popen(args, creationflags=DETACHED,
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        _launched_pids[p.get("名字")] = proc.pid
        return "OK" + (f"（CDP {port}）" if port else "")
    elif t == "web":
        browser = p.get("浏览器") or "msedge"
        exe = _find_browser(browser)
        if not exe:
            return (f"找不到浏览器（{browser}）；请确认已安装 Edge/Chrome 等，"
                    "或在添加时『扫描进程』选择正确的浏览器")
        args = [exe]
        if port:
            ud = os.path.join(EDGE_CDP_DIR, f"{browser}_cdp_{port}")
            args += [f"--remote-debugging-port={port}", "--remote-allow-origins=*",
                     f"--user-data-dir={ud}"]
        args.append(p.get("url"))
        proc = subprocess.Popen(args, creationflags=DETACHED,
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        _launched_pids[p.get("名字")] = proc.pid
        return f"OK ({browser})" + (f"（CDP {port}）" if port else "")
    return "未知类型"


def _terminate_tree(pid):
    """终止进程及其所有子进程（浏览器多为多进程，需一并结束）。"""
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    try:
        children = proc.children(recursive=True)
    except Exception:
        children = []
    for c in children:
        try:
            c.terminate()
        except Exception:
            pass
    try:
        proc.terminate()
    except Exception:
        pass


def kill(p):
    """关闭选手：优先精确关闭本程序启动的实例；否则按进程名关闭（会关掉同名全部）。"""
    name = p.get("名字")
    pid = _launched_pids.get(name)
    if pid:
        _terminate_tree(pid)
        _launched_pids.pop(name, None)
        return
    n = p.get("进程名") or name
    if not n:
        return
    for x in psutil.process_iter(['name', 'pid']):
        if (x.info['name'] or "").lower().startswith(n.lower()):
            try:
                psutil.Process(x.info['pid']).terminate()
            except Exception:
                pass
