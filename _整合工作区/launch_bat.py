"""用宽字符 API 启动中文名 bat（规避 cmd 编码问题），并尝试脱离作业对象以便常驻。"""
import subprocess, os, time, sys
import psutil

ROOT = r"F:\赛马23环整合工作室\程序2改装版"
BAT = "启动_主界面.bat"

FLAGS = 0x00000008 | 0x00000200 | 0x01000000  # DETACHED_PROCESS | NEW_PROCESS_GROUP | BREAKAWAY_FROM_JOB
try:
    p = subprocess.Popen(["cmd.exe", "/c", BAT], cwd=ROOT, creationflags=FLAGS,
                         stdin=subprocess.DEVNULL,
                         stdout=open(r"F:\赛马23环整合工作室\_整合工作区\bat_out.log", "wb"),
                         stderr=subprocess.STDOUT)
    print("bat launched, cmd pid", p.pid)
except Exception as e:
    print("breakaway failed:", e)
    p = subprocess.Popen(["cmd.exe", "/c", BAT], cwd=ROOT,
                         creationflags=0x00000008 | 0x00000200,
                         stdin=subprocess.DEVNULL,
                         stdout=open(r"F:\赛马23环整合工作室\_整合工作区\bat_out.log", "wb"),
                         stderr=subprocess.STDOUT)
    print("bat launched (no breakaway), cmd pid", p.pid)

time.sleep(16)
print("--- collab_app 进程 ---")
for q in psutil.process_iter(['name', 'cmdline']):
    cl = " ".join(q.info['cmdline'] or [])
    if 'collab_app' in cl:
        try:
            cwd = q.cwd()
        except Exception:
            cwd = '?'
        print(" ", q.pid, "|", cwd, "|", cl[:100])
