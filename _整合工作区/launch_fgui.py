"""分离式启动 F 盘 32流程版 主界面（不阻塞、独立进程组）。"""
import subprocess, os, sys, time

ROOT = r"F:\赛马23环整合工作室\程序2改装版"
VPY = os.path.join(ROOT, "windows-use", ".venv", "Scripts", "python.exe")
CODE = os.path.join(ROOT, "app", "collab_app.py")
OUT = r"F:\赛马23环整合工作室\_整合工作区\fgui_out.log"
ERR = r"F:\赛马23环整合工作室\_整合工作区\fgui_err.log"

DETACHED = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

fo = open(OUT, "wb")
fe = open(ERR, "wb")
p = subprocess.Popen([VPY, CODE], cwd=ROOT, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL,
                     creationflags=DETACHED)
print("launched pid", p.pid, "cwd", ROOT)
time.sleep(10)
print("alive after 10s:", p.poll() is None, "rc:", p.poll())
