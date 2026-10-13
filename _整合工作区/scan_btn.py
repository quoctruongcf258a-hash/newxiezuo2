import ctypes
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

CX, CY = 555, 568

def get_pixel(hdc, x, y):
    c = gdi32.GetPixel(hdc, x, y)
    if c == -1: return (0, 0, 0)
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)

hdc = user32.GetDC(0)
try:
    print(f"扫描 ({CX}, {CY}) 周围 ±30 区域，找蓝色像素")
    print("=" * 60)
    blue_pts = []
    for dy in range(-30, 31, 3):
        row = []
        for dx in range(-30, 31, 3):
            r, g, b = get_pixel(hdc, CX+dx, CY+dy)
            if b > 180 and b > r + 30 and b > g + 15:
                row.append("B")
                blue_pts.append((CX+dx, CY+dy, r, g, b))
            elif r > 220 and g > 220 and b > 220:
                row.append("W")
            elif r < 60 and g < 60 and b < 60:
                row.append(".")
            else:
                row.append("-")
        print("".join(row))
    print("=" * 60)
    print(f"找到 {len(blue_pts)} 个蓝色像素：")
    if blue_pts:
        xs = [p[0] for p in blue_pts]
        ys = [p[1] for p in blue_pts]
        print(f"  x 范围：{min(xs)} ~ {max(xs)}")
        print(f"  y 范围：{min(ys)} ~ {max(ys)}")
        cx = (min(xs) + max(xs)) // 2
        cy = (min(ys) + max(ys)) // 2
        print(f"  蓝色区域中心：({cx}, {cy})")
    else:
        print("  ❌ 没有蓝色像素——坐标可能偏了，或按钮不是蓝色")
finally:
    user32.ReleaseDC(0, hdc)
