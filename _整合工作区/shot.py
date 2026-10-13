import win32gui, win32ui, win32con, win32process
from PIL import Image
import sys

target = sys.argv[1] if len(sys.argv) > 1 else "协同写作控制台"
found = []

def cb(h, _):
    if win32gui.IsWindowVisible(h):
        t = win32gui.GetWindowText(h)
        if target in t:
            found.append((h, t))
    return True

win32gui.EnumWindows(cb, None)
if not found:
    print("NO WINDOW")
    sys.exit(1)

h, t = found[0]
print("window:", t)
win32gui.SetForegroundWindow(h)
import time; time.sleep(1)
l, tp, r, b = win32gui.GetWindowRect(h)
w, hh = r - l, b - tp
print("rect", l, tp, r, b, "size", w, hh)
hdc = win32gui.GetWindowDC(h)
udc = win32ui.CreateDCFromHandle(hdc)
mem = udc.CreateCompatibleDC()
bmp = win32ui.CreateBitmap()
bmp.CreateCompatibleBitmap(udc, w, hh)
mem.SelectObject(bmp)
mem.BitBlt((0, 0), (w, hh), udc, (0, 0), win32con.SRCCOPY)
info = bmp.GetInfo()
bits = bmp.GetBitmapBits(True)
img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]), bits, "raw", "BGRX", 0, 1)
out = (sys.argv[2] if len(sys.argv) > 2 else r"F:\赛马23环整合工作室\_整合工作区\ui_shot.png")
img.save(out)
print("saved", out, img.size)
win32gui.ReleaseDC(h, hdc)
