import time, ctypes
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

CX, CY = 555, 568

def get_pixel(hdc, x, y):
    c = gdi32.GetPixel(hdc, x, y)
    if c == -1: return (0, 0, 0)
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)

def sample():
    hdc = user32.GetDC(0)
    try:
        blue = white = 0
        # 中心 3×3 + 环形 8 点
        pts = [(0,0), (-4,0), (4,0), (0,-4), (0,4),
               (-6,-6), (6,-6), (-6,6), (6,6)]
        for dx, dy in pts:
            r, g, b = get_pixel(hdc, CX+dx, CY+dy)
            if b > 180 and b > r + 30 and b > g + 15: blue += 1
            elif r > 220 and g > 220 and b > 220: white += 1
        return blue, white
    finally:
        user32.ReleaseDC(0, hdc)

def classify(blue, white):
    if blue >= 3: return "待发送(蓝)"
    if white >= 2: return "运行中(白)"
    return "空闲(灰)"

print(f"监控豆包 ({CX}, {CY}) · 每秒刷新 · Ctrl+C 停")
print("请严格按顺序操作：")
print("  1) 现在别动，等 5 秒看空闲")
print("  2) 在输入框打字，看是否变【待发送】")
print("  3) 按下 Enter 发送后，立刻观察 30 秒")
print("  4) 等豆包答完，看是否变回【空闲】")
print()
while True:
    blue, white = sample()
    state = classify(blue, white)
    print(f"[{time.strftime('%H:%M:%S')}]  {state:12}  蓝={blue}  白={white}")
    time.sleep(1)
