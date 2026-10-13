import ctypes
import ctypes.wintypes as wt
import time
import sys

try:
    import msvcrt
except ImportError:
    msvcrt = None

user32 = ctypes.windll.user32

# ── 获取鼠标位置 ──
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_pos():
    p = POINT()
    user32.GetCursorPos(ctypes.byref(p))
    return p.x, p.y

# ── 获取屏幕像素颜色 ──
gdi32 = ctypes.windll.gdi32
def get_pixel_color(x, y):
    hdc = user32.GetDC(0)
    try:
        color = gdi32.GetPixel(hdc, x, y)
        if color == -1:
            return (0, 0, 0)
        r = color & 0xFF
        g = (color >> 8) & 0xFF
        b = (color >> 16) & 0xFF
        return (r, g, b)
    finally:
        user32.ReleaseDC(0, hdc)

# ── 获取鼠标所在窗口标题 ──
def get_window_title():
    hwnd = user32.WindowFromPoint(POINT(*get_pos()))
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, buf, 256)
    return buf.value or "(无标题)"

# ── 主循环 ──
recorded = []

print("=" * 70)
print("坐标定位器 · Ctrl+C 退出")
print("=" * 70)
print("把鼠标移到目标位置，屏幕会实时显示：")
print("  · 坐标 (X, Y)")
print("  · 该点像素颜色 RGB + 十六进制")
print("  · 所在窗口标题")
print()
print("按 F1 记录当前坐标到列表")
print("按 F2 清空已记录")
print("按 F3 打印已记录列表")
print("=" * 70)
print()

last_line_len = 0
while True:
    x, y = get_pos()
    r, g, b = get_pixel_color(x, y)
    title = get_window_title()

    # 检测按键
    if msvcrt and msvcrt.kbhit():
        k = msvcrt.getch()
        if k in (b"\x00", b"\xe0"):  # 扩展键
            k2 = msvcrt.getch()
            if k2 == b";":    # F1
                recorded.append((x, y, (r, g, b), title))
                print(f"\n✅ 已记录 #{len(recorded)}：({x}, {y})  RGB=({r},{g},{b})  [{title[:40]}]")
            elif k2 == b"<":  # F2
                recorded.clear()
                print("\n🗑  已清空记录")
            elif k2 == b"=":  # F3
                print(f"\n📋 已记录 {len(recorded)} 个坐标：")
                for i, (rx, ry, rgb, t) in enumerate(recorded, 1):
                    print(f"   #{i}  ({rx}, {ry})  RGB={rgb}  [{t[:50]}]")
                print()
        elif k == b"\x1b":  # ESC
            print("\n\n退出。")
            break

    # 拼接行
    hex_color = f"#{r:02X}{g:02X}{b:02X}"
    line = f"\r({x:5d}, {y:5d})   RGB=({r:3d},{g:3d},{b:3d}) {hex_color}   窗口: {title[:40]}"
    pad = " " * max(0, last_line_len - len(line))
    sys.stdout.write(line + pad)
    sys.stdout.flush()
    last_line_len = len(line)

    time.sleep(0.05)