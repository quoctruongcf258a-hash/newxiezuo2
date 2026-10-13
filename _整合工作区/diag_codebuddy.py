# -*- coding: utf-8 -*-
"""排查 CodeBuddy(CDP) 起不来：配置 / 端口 / 进程。"""
import io, json, os, sys, socket

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CFG = r"F:\赛马23环整合工作室\程序2改装版\rules\ai_apps.json"
d = json.load(open(CFG, encoding="utf-8"))
if isinstance(d, list):
    apps = d
elif isinstance(d, dict):
    apps = d.get("AI") or d.get("apps") or list(d.values())
else:
    apps = []
if isinstance(apps, dict):
    apps = list(apps.values())

print("=== 配置里含 codebuddy 的条目 ===")
hits = []
for a in apps:
    if not isinstance(a, dict):
        continue
    if "codebuddy" in str(a.get("名字", "")).lower() or "codebuddy" in json.dumps(a).lower():
        hits.append(a)
        print(json.dumps(a, ensure_ascii=False, indent=2))

print("\n=== 端口探测 ===")


def probe(port):
    s = socket.socket()
    s.settimeout(0.4)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except Exception:
        return False
    finally:
        s.close()


ports = sorted({a.get("cdp_port") for a in apps if isinstance(a, dict) and a.get("cdp_port")})
for p in ports:
    print("  %s : %s" % (p, "OPEN(绿灯)" if probe(p) else "closed(红灯)"))

print("\n=== exe 路径是否存在 ===")
for a in hits:
    exe = a.get("exe")
    print("  exe=%s" % exe)
    if exe:
        print("   exists=%s" % os.path.exists(exe))

print("\n=== 全盘找 CodeBuddy 可执行 ===")
cands = []
for base in (r"C:\Users\Administrator\AppData\Local\Programs",
             r"C:\Program Files", r"C:\Program Files (x86)",
             r"C:\Users\Administrator\AppData\Local"):
    for root, dirs, files in os.walk(base):
        depth = root[len(base):].count(os.sep)
        if depth > 3:
            dirs[:] = []
            continue
        low = root.lower()
        if "codebuddy" in low and any(f.lower().endswith(".exe") for f in files):
            for f in files:
                if f.lower().endswith(".exe"):
                    cands.append(os.path.join(root, f))
        if len(cands) > 20:
            break
print("\n".join(cands[:20]) or "  (未在常见安装目录找到 codebuddy exe)")