# -*- coding: utf-8 -*-
"""验证：清掉 ELECTRON_/VSCODE_ 污染变量后，能否带 CDP 端口拉起 CodeBuddy CN。"""
import io, os, socket, subprocess, sys, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
APP = r"F:\赛马23环整合工作室\程序2改装版\app"
sys.path.insert(0, APP)
import players

print("=== 当前环境（启动前）===")
bad = {k: v for k, v in os.environ.items()
       if k.upper().startswith("ELECTRON_") or k.upper().startswith("VSCODE_")}
print("  污染变量数:", len(bad), "→", list(bad)[:6])

env = players._clean_env()
print("=== _clean_env 后 ===")
left = [k for k in env if k.upper().startswith("ELECTRON_") or k.upper().startswith("VSCODE_")]
print("  残留:", left or "无")
print("  Path 是否保留:", bool(env.get("Path")))

EXE = r"C:\Users\Administrator\AppData\Local\Programs\CodeBuddy CN\CodeBuddy CN.exe"
PORT = 9223
p = {"名字": "CodeBuddy", "类型": "electron", "进程名": "CodeBuddy CN", "exe": EXE,
     "cdp_port": PORT}
print("\n=== 用 players.launch 启动 ===")
print("  结果:", players.launch(p))

def alive(port, t=0.4):
    s = socket.socket(); s.settimeout(t)
    try:
        s.connect(("127.0.0.1", port)); return True
    except Exception:
        return False
    finally:
        s.close()

ok = False
for i in range(20):
    time.sleep(1.5)
    if alive(PORT):
        ok = True
        print("  ✅ 端口 %d 已监听（等待 %.1fs）" % (PORT, i * 1.5 + 1.5))
        break
if not ok:
    print("  ❌ 端口 %d 仍未监听" % PORT)

# 读取 CDP 版本，确认真的可连
if ok:
    import urllib.request
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=3) as r:
            import json
            d = json.loads(r.read().decode("utf-8", "replace"))
        print("  CDP /json/version:", d.get("Browser"), "|", d.get("webSocketDebuggerUrl", "")[:60])
    except Exception as e:
        print("  CDP 查询失败:", e)