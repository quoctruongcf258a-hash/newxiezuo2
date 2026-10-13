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
    print(f"扫描 ({CX}, {CY}) 周围 ±40 区域")
    print("图例：B=蓝 W=白 .=暗 -=其他")
    print("=" * 60)
    for dy in range(-40, 41, 4):
        row = []
        for dx in range(-40, 41, 4):
            r, g, b = get_pixel(hdc, CX+dx, CY+dy)
            if b > 180 and b > r + 30 and b > g + 15:
                row.append("B")
            elif r > 220 and g > 220 and b > 220:
                row.append("W")
            elif r < 80 and g < 80 and b < 80:
                row.append(".")
            else:
                row.append("-")
        print("".join(row))
    print("=" * 60)
finally:
    user32.ReleaseDC(0, hdc)
