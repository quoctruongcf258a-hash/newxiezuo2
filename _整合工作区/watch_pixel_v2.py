import time
import ctypes

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

X, Y = 1833, 864

def get_pixel(x, y):
    hdc = user32.GetDC(0)
    try:
        c = gdi32.GetPixel(hdc, x, y)
        if c == -1: return (0,0,0)
        return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)
    finally:
        user32.ReleaseDC(0, hdc)

print(f"监控 ({X}, {Y}) · 每 0.5 秒打印 · Ctrl+C 停")
print()
print("操作：")
print("  1) 什么都不做，让鼠标远离按钮 —— 记空闲色")
print("  2) 打字 —— 记待发送色")
print("  3) 点发送 —— 记运行色")
print("  4) 等答完 —— 看变回什么色")
print()

while True:
    r, g, b = get_pixel(X, Y)
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}]  RGB=({r:3d},{g:3d},{b:3d})  HEX=#{r:02X}{g:02X}{b:02X}")
    time.sleep(0.5)