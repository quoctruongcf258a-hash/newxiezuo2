"""启动所有 AI（带 CDP）+ 自动网格排列"""
import subprocess, time, psutil, os, json
import pygetwindow as gw

# 屏幕大小（先探测）
import ctypes
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
SW = user32.GetSystemMetrics(0)
SH = user32.GetSystemMetrics(1)
print(f"屏幕: {SW}x{SH}")

# 要启动 + 排列的 AI
APPS = [
    # (名字, 进程名, exe路径, CDP端口)
    ("CodeBuddy",  "CodeBuddy CN", r"C:\Users\Administrator\AppData\Local\Programs\CodeBuddy CN\CodeBuddy CN.exe", 9223),
    ("QUEST",      "QoderCN",      r"C:\Users\Administrator\AppData\Local\Programs\QoderCN\QoderCN.exe",         9224),
    ("TraeWork",   "TRAE SOLO CN", r"G:\TRAE SOLO CN\TRAE SOLO CN.exe",                                            9225),
    ("Qianwen",    "qianwen",      r"C:\Program Files\QianwenApp\qianwen.exe",                                     9226),
    ("WorkBuddy",  "WorkBuddy",    r"F:\Program\WorkBuddy.exe",                                                    9227),
    ("ZCode",      "ZCode",        r"C:\Program Files\ZCode\ZCode.exe",                                            9228),
    ("Doubao",     "Doubao",       r"F:\Program Files\com.tencent.pcgame.doubao\Doubao\app\Doubao.exe",            None),
]

print("\n=== 第一步：关闭旧进程 ===")
for name, proc, exe, port in APPS:
    n = 0
    for x in psutil.process_iter(['name','pid']):
        if (x.info['name'] or "").lower().startswith(proc.lower()):
            try: psutil.Process(x.info['pid']).terminate(); n += 1
            except: pass
    if n: print(f"  关闭 {name}: {n} 进程")
time.sleep(3)

print("\n=== 第二步：启动 ===")
for name, proc, exe, port in APPS:
    if not os.path.exists(exe):
        print(f"  ❌ {name}: exe 不存在 {exe}"); continue
    args = [exe]
    if port:
        args += [f"--remote-debugging-port={port}", "--remote-allow-origins=*"]
    subprocess.Popen(args)
    print(f"  🚀 {name} 启动" + (f"（CDP {port}）" if port else ""))
    time.sleep(3.5)

print("\n=== 第三步：等窗口就绪 ===")
time.sleep(12)

print("\n=== 第四步：网格排列 ===")
# 4 列 x 2 行
COLS = 4
ROWS = 2
W = SW // COLS
H = SH // ROWS
print(f"每个窗口: {W}x{H}")

positions = []
for r in range(ROWS):
    for c in range(COLS):
        positions.append((c * W, r * H, W, H))

# 找所有 AI 窗口
def find_windows():
    found = []
    for name, proc, exe, port in APPS:
        pids = set()
        for x in psutil.process_iter(['name','pid']):
            if (x.info['name'] or "").lower().startswith(proc.lower()):
                pids.add(x.info['pid'])
        wins = []
        import win32process
        for w in gw.getAllWindows():
            if not w.title or w.width < 200 or w.height < 200: continue
            if w.left < -10000: continue
            try:
                _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
                if wp in pids:
                    wins.append(w)
            except: pass
        if wins:
            # 选最大的那个窗口
            wins.sort(key=lambda w: w.width * w.height, reverse=True)
            found.append((name, wins[0]))
    return found

wins = find_windows()
print(f"\n找到 {len(wins)} 个 AI 窗口")

for i, (name, w) in enumerate(wins):
    if i >= len(positions): break
    x, y, ww, hh = positions[i]
    try:
        w.restore() if w.isMinimized else None
        w.moveTo(x, y)
        w.resizeTo(ww, hh)
        time.sleep(0.4)
        print(f"  [{name}] → ({x},{y}) {ww}x{hh}")
    except Exception as e:
        print(f"  [{name}] 失败: {e}")

print("\n=== 第五步：验证 CDP ===")
import urllib.request
for name, proc, exe, port in APPS:
    if not port: continue
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3) as f:
            n = len([t for t in json.load(f) if t.get("type")=="page"])
        print(f"  ✅ {name}  端口 {port}  ({n} 页面)")
    except:
        print(f"  ❌ {name}  端口 {port}  连不上")

print("\n完成！")
