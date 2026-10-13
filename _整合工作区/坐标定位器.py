import ctypes
import time
import sys

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

user32 = ctypes.windll.user32

print("坐标定位器已启动")
print("移动鼠标，屏幕实时显示坐标")
print("按 Ctrl+C 停止")
print()

last_len = 0
while True:
    p = POINT()
    user32.GetCursorPos(ctypes.byref(p))
    line = f"\r({p.x}, {p.y})"
    pad = " " * max(0, last_len - len(line))
    sys.stdout.write(line + pad)
    sys.stdout.flush()
    last_len = len(line)
    time.sleep(0.05)