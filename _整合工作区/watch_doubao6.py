import time, ctypes
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

CX, CY = 555, 564

def get_pixel(hdc, x, y):
    c = gdi32.GetPixel(hdc, x, y)
    if c == -1:
        return (0, 0, 0)
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)

def sample():
    hdc = user32.GetDC(0)
    try:
        # 只采 5 个点：中心 + 上下左右 12px
        pts = [(CX, CY), (CX-12, CY), (CX+12, CY), (CX, CY-12), (CX, CY+12)]
        blue = white = 0
        for x, y in pts:
            r, g, b = get_pixel(hdc, x, y)
            if b > 180 and b > r + 30 and b > g + 15:
                blue += 1
            elif r > 220 and g > 220 and b > 220:
                white += 1
        return blue, white
    finally:
        user32.ReleaseDC(0, hdc)

print(f"监控豆包 ({CX}, {CY}) 5点采样 · 每秒刷新 · Ctrl+C 停")
print()
while True:
    t0 = time.time()
    blue, white = sample()
    if blue >= 2:
        state = "待发送(蓝)"
    elif white >= 2:
        state = "运行中(白)"
    else:
        state = "空闲(灰)"
    ms = (time.time() - t0) * 1000
    print(f"[{time.strftime('%H:%M:%S')}]  {state}   蓝={blue}  白={white}   ({ms:.0f}ms)")
    time.sleep(max(0, 1 - (time.time() - t0)))
