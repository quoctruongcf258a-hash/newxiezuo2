"""一次调用内完成：启动 F 盘 32流程版主界面 -> 等待 -> 枚举窗口 -> 截图 -> 收尾。"""
import subprocess, os, sys, time
import win32gui, win32ui, win32con, win32process
from PIL import Image

ROOT = r"F:\赛马23环整合工作室\程序2改装版"
VPY = os.path.join(ROOT, "windows-use", ".venv", "Scripts", "python.exe")
CODE = os.path.join(ROOT, "app", "collab_app.py")
OUT = r"F:\赛马23环整合工作室\_整合工作区\fgui_out.log"
ERR = r"F:\赛马23环整合工作室\_整合工作区\fgui_err.log"
SHOT = r"F:\赛马23环整合工作室\_整合工作区\fgui_shot.png"

fo, fe = open(OUT, "wb"), open(ERR, "wb")
p = subprocess.Popen([VPY, CODE], cwd=ROOT, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL)
print("launched pid", p.pid)

target_pid = p.pid
wins = []
for i in range(30):
    time.sleep(1)
    if p.poll() is not None:
        print("!! process exited early rc=", p.poll(), "after", i + 1, "s")
        break
    wins = []
    def cb(h, _):
        try:
            _, pid = win32process.GetWindowThreadProcessId(h)
        except Exception:
            return True
        if pid == target_pid:
            wins.append((h, win32gui.IsWindowVisible(h), win32gui.GetWindowText(h)))
        return True
    win32gui.EnumWindows(cb, None)
    vis = [w for w in wins if w[1] and w[2]]
    if vis:
        print("window ready after", i + 1, "s")
        break

print("--- 该进程窗口 ---")
for h, v, t in wins:
    print("  hwnd", h, "visible", v, "title", repr(t))

vis = [w for w in wins if w[1] and w[2]]
if vis:
    h, _, t = vis[0]
    try:
        win32gui.SetForegroundWindow(h)
    except Exception:
        pass
    time.sleep(1.5)
    l, tp, r, b = win32gui.GetWindowRect(h)
    w, hh = r - l, b - tp
    hdc = win32gui.GetWindowDC(h)
    udc = win32ui.CreateDCFromHandle(hdc)
    mem = udc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(udc, w, hh)
    mem.SelectObject(bmp)
    mem.BitBlt((0, 0), (w, hh), udc, (0, 0), win32con.SRCCOPY)
    info = bmp.GetInfo()
    img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]),
                           bmp.GetBitmapBits(True), "raw", "BGRX", 0, 1)
    img.save(SHOT)
    print("saved", SHOT, img.size, "title:", t)
    win32gui.ReleaseDC(h, hdc)
else:
    print("NO VISIBLE WINDOW")

p.terminate()
try:
    p.wait(timeout=8)
except Exception:
    p.kill()
print("child stopped rc=", p.poll())
