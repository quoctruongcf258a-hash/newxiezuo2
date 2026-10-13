import time, ctypes
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
CX, CY = 563, 569
def get_pixel(hdc, x, y):
    c = gdi32.GetPixel(hdc, x, y)
    if c == -1: return (0, 0, 0)
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)
def sample():
    hdc = user32.GetDC(0)
    try:
        blue = white = dark = gray = total = 0
        for dy in range(-12, 13, 3):
            for dx in range(-12, 13, 3):
                r, g, b = get_pixel(hdc, CX+dx, CY+dy)
                total += 1
                if b > 180 and b > r + 30 and b > g + 15:
                    blue += 1
                elif r > 220 and g > 220 and b > 220:
                    white += 1
                elif r < 80 and g < 80 and b < 80:
                    dark += 1
                else:
                    gray += 1
        return blue, white, dark, gray, total
    finally:
        user32.ReleaseDC(0, hdc)
def classify(blue, white, dark, gray, total):
    if blue > total * 0.2:  return "待发送(蓝)"
    if dark > total * 0.25: return "空闲(深图标)"
    if white > total * 0.8: return "空白"
    return "其他"
print(f"监控豆包 ({CX}, {CY}) · 每秒刷新 · Ctrl+C 停")
print("操作顺序：")
print("  1) 空闲 10 秒 —— 看基线")
print("  2) 打字 —— 看蓝色圆出现")
print("  3) 发送长任务 —— 看运行中")
print("  4) 等答完 —— 看变回什么")
print()
while True:
    blue, white, dark, gray, total = sample()
    state = classify(blue, white, dark, gray, total)
    print(f"[{time.strftime('%H:%M:%S')}]  {state:14}  蓝={blue:2d}  白={white:2d}  暗={dark:2d}  灰={gray:2d}  总={total}")
    time.sleep(1)
