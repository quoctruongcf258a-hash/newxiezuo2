import ctypes, time, sys
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_pixel(x, y):
    hdc = user32.GetDC(0)
    try:
        c = gdi32.GetPixel(hdc, x, y)
        if c == -1: return (0,0,0)
        return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)
    finally:
        user32.ReleaseDC(0, hdc)

print("鼠标跟踪 · 移到哪显示哪的坐标和颜色 · Ctrl+C 停")
print()
last = None
while True:
    p = POINT()
    user32.GetCursorPos(ctypes.byref(p))
    r, g, b = get_pixel(p.x, p.y)
    line = f"({p.x:5d}, {p.y:5d})  RGB=({r:3d},{g:3d},{b:3d})  HEX=#{r:02X}{g:02X}{b:02X}"
    if line != last:
        print(line)
        last = line
    time.sleep(0.2)
