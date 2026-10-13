import time, ctypes
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# 按钮中心坐标
CX, CY = 555, 564
# 采样半径（按钮大约 50px，取 ±22 覆盖整个圆）
R = 22

def get_pixel(x, y):
    hdc = user32.GetDC(0)
    try:
        c = gdi32.GetPixel(hdc, x, y)
        return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF) if c != -1 else (0,0,0)
    finally:
        user32.ReleaseDC(0, hdc)

def sample(cx, cy, r):
    """采样按钮区域，返回 (蓝色像素数, 白色像素数, 总像素数)"""
    blue = white = total = 0
    for dx in range(-r, r+1, 2):
        for dy in range(-r, r+1, 2):
            x, y = cx+dx, cy+dy
            pr, pg, pb = get_pixel(x, y)
            total += 1
            # 蓝色：b 明显大于 r 和 g
            if pb > 180 and pb > pr + 30 and pb > pg + 15:
                blue += 1
            # 白色：r/g/b 都接近 255
            elif pr > 220 and pg > 220 and pb > 220:
                white += 1
    return blue, white, total

def classify(blue, white, total):
    if blue / total > 0.15:
        return "待发送(蓝)", blue, white
    if white / total > 0.10:
        return "运行中(白)", blue, white
    return "空闲(灰)", blue, white

print(f"监控豆包按钮 ({CX}, {CY}) 区域 R={R} · 每秒刷新 · Ctrl+C 停")
print()
print("操作：1) 空闲10秒  2) 打字  3) 发送  4) 等答完")
print()
while True:
    blue, white, total = sample(CX, CY, R)
    state, _, _ = classify(blue, white, total)
    print(f"[{time.strftime('%H:%M:%S')}]  {state:10}  蓝={blue:3d}  白={white:3d}  总={total}")
    time.sleep(1)
