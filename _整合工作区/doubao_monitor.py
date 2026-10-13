import time, ctypes, sys
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# 关键差异点（从差异分析结果中挑选）
IDLE_PT = (559, 565)      # 空闲时浅色，运行中深色
GREEN_PT = (547, 565)     # 运行中变绿
BLUE_PT = (571, 577)      # 待发送变蓝

def get_pixel(hdc, x, y):
    c = gdi32.GetPixel(hdc, x, y)
    if c == -1: return (0,0,0)
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)

def is_green(rgb): 
    r,g,b = rgb
    return g > 150 and g > r + 80 and g > b + 40

def is_blue(rgb):
    r,g,b = rgb
    return b > 200 and b > r + 100 and g < 150

def is_dark(rgb):
    r,g,b = rgb
    return r < 80 and g < 80 and b < 80

def classify(hdc):
    idle_rgb = get_pixel(hdc, *IDLE_PT)
    green_rgb = get_pixel(hdc, *GREEN_PT)
    blue_rgb = get_pixel(hdc, *BLUE_PT)

    if is_green(green_rgb):
        return "运行中", idle_rgb, green_rgb, blue_rgb
    if is_blue(blue_rgb):
        return "待发送", idle_rgb, green_rgb, blue_rgb
    if is_dark(idle_rgb):
        return "运行中", idle_rgb, green_rgb, blue_rgb
    return "空闲", idle_rgb, green_rgb, blue_rgb

print("豆包状态监控 · 每秒刷新 · Ctrl+C 停")
print("空闲10s → 打字 → 发送 → 等答完")
print("-" * 78)
print(f"{'时间':<10} {'状态':<8} idle点          绿点            蓝点")
print("-" * 78)

last = None
while True:
    hdc = user32.GetDC(0)
    try:
        state, a, b, c = classify(hdc)
    finally:
        user32.ReleaseDC(0, hdc)

    line = f"{state}"
    if line != last:
        ts = time.strftime('%H:%M:%S')
        print(f"{ts:<10} {state:<8} {str(a):<16} {str(b):<16} {str(c):<16}")
        last = line

    time.sleep(1)
