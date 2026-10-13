import time, ctypes, sys
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

IDLE_PT = (559, 565)
GREEN_PT = (547, 565)
BLUE_PT = (571, 577)

def get_pixel(hdc, x, y):
    c = gdi32.GetPixel(hdc, x, y)
    if c == -1: return (0,0,0)
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)

def classify(idle_rgb, green_rgb, blue_rgb):
    r, g, b = idle_rgb
    # 深蓝 = 待发送
    if b > 220 and r < 60 and g < 130:
        return "待发送"
    # 浅蓝 / 绿 = 运行中
    if b > 200 and r > 60 and r < 200 and g > 120:
        return "运行中"
    if g > 150 and g > r + 80:
        return "运行中"
    # 灰白 = 空闲
    if r > 220 and g > 220 and b > 220:
        return "空闲"
    # 其他
    return f"?({r},{g},{b})"

print("豆包状态监控 · 每秒刷新 · Ctrl+C 停")
print("空闲10s → 打字 → 发送 → 等答完")
print("-" * 90)
print(f"{'时间':<10} {'状态':<10} idle点          绿点            蓝点")
print("-" * 90)

while True:
    hdc = user32.GetDC(0)
    try:
        a = get_pixel(hdc, *IDLE_PT)
        b = get_pixel(hdc, *GREEN_PT)
        c = get_pixel(hdc, *BLUE_PT)
    finally:
        user32.ReleaseDC(0, hdc)
    state = classify(a, b, c)
    ts = time.strftime('%H:%M:%S')
    print(f"{ts:<10} {state:<10} {str(a):<16} {str(b):<16} {str(c):<16}")
    time.sleep(1)
