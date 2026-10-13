import time
import ctypes
import sys

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# ═══════════ 填你要监控的坐标 ═══════════
X, Y = 1833, 864
# ═══════════════════════════════════════

def get_pixel(x, y):
    hdc = user32.GetDC(0)
    try:
        c = gdi32.GetPixel(hdc, x, y)
        if c == -1:
            return (0, 0, 0)
        r = c & 0xFF
        g = (c >> 8) & 0xFF
        b = (c >> 16) & 0xFF
        return (r, g, b)
    finally:
        user32.ReleaseDC(0, hdc)

print("=" * 70)
print(f"监控坐标 ({X}, {Y}) 的像素颜色")
print("=" * 70)
print("操作顺序：")
print("  1. 什么都不做 —— 看空闲态颜色")
print("  2. 输入框打字 —— 看按钮变紫")
print("  3. 点发送 —— 看按钮变方块")
print("  4. 等答完 —— 看变回灰色")
print("=" * 70)
print()

last = None
while True:
    r, g, b = get_pixel(X, Y)
    cur = (r, g, b)
    if cur != last:
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}]  颜色变化 →  RGB=({r:3d},{g:3d},{b:3d})  HEX=#{r:02X}{g:02X}{b:02X}")
        last = cur
    time.sleep(0.3)