import time, ctypes
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

CX, CY = 555, 568
R = 12
STEP = 4   # 7×7 = 49 个采样点

def get_pixel(hdc, x, y):
    c = gdi32.GetPixel(hdc, x, y)
    if c == -1: return (0, 0, 0)
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)

def sample():
    hdc = user32.GetDC(0)
    try:
        blue = white = dark = total = 0
        for dy in range(-R, R+1, STEP):
            for dx in range(-R, R+1, STEP):
                r, g, b = get_pixel(hdc, CX+dx, CY+dy)
                total += 1
                if b > 180 and b > r + 30 and b > g + 15:
                    blue += 1
                elif r > 220 and g > 220 and b > 220:
                    white += 1
                elif r < 80 and g < 80 and b < 80:
                    dark += 1
        return blue, white, dark, total
    finally:
        user32.ReleaseDC(0, hdc)

def classify(blue, white, dark, total):
    if blue > total * 0.15:
        return "待发送(蓝)"
    if white > total * 0.15:
        return "运行中(白)"
    return "空闲(灰)"

print(f"监控豆包 ({CX}, {CY}) R={R} · 每秒刷新 · Ctrl+C 停")
print()
while True:
    t0 = time.time()
    blue, white, dark, total = sample()
    state = classify(blue, white, dark, total)
    ms = (time.time() - t0) * 1000
    print(f"[{time.strftime('%H:%M:%S')}]  {state:10}  蓝={blue:3d}  白={white:3d}  暗={dark:3d}  总={total:3d}  ({ms:.0f}ms)")
    time.sleep(max(0, 1 - (time.time() - t0)))
