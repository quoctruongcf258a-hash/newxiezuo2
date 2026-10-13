# -*- coding: utf-8 -*-
"""
GUI 启动探针：真正运行 collab_app.py 若干秒，判断是"弹窗成功"还是"启动即崩"。
不依赖 cmd，直接用 subprocess。
"""
import subprocess, sys, os, time

VPY_CANDIDATES = [
    r"F:\赛马23环整合工作室\程序2改装版\windows-use\.venv\Scripts\python.exe",
    r"C:\mai\multi-ai-pipeline_webtest\windows-use\.venv\Scripts\python.exe",
]
CWD = r"F:\赛马23环整合工作室\程序2改装版"
SCRIPT = sys.argv[1] if len(sys.argv) > 1 else r"app\collab_app.py"
WAIT = int(sys.argv[2]) if len(sys.argv) > 2 else 12

vpy = None
for c in VPY_CANDIDATES:
    if os.path.exists(c):
        vpy = c
        break
if not vpy:
    print("RESULT: 找不到任何可用解释器")
    sys.exit(1)

print(f"解释器 : {vpy}")
print(f"工作目录: {CWD}")
print(f"脚本   : {SCRIPT}")
print(f"观察 {WAIT} 秒...\n")

log = os.path.join(CWD, "_gui_probe.log")
with open(log, "w", encoding="utf-8", errors="replace") as f:
    p = subprocess.Popen([vpy, SCRIPT], cwd=CWD, stdout=f, stderr=subprocess.STDOUT)

time.sleep(WAIT)
alive = p.poll() is None
if alive:
    print("RESULT: 进程仍在运行 -> 窗口应已弹出(未崩溃)")
    p.kill()
    try:
        p.wait(timeout=5)
    except Exception:
        p.terminate()
else:
    print(f"RESULT: 进程已退出 -> 启动即崩，退出码 = {p.returncode}")

print("\n===== 程序输出/报错 =====")
try:
    txt = open(log, encoding="utf-8", errors="replace").read()
    print(txt if txt.strip() else "(无输出——说明 GUI 正常静默运行，或崩溃无 traceback)")
except Exception as e:
    print("读日志失败:", e)
