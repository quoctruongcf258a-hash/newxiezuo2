import time, ctypes, sys
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# 四角坐标
X0, Y0 = 651, 976
X1, Y1 = 680, 1003
STEP = 2

def get_pixel(hdc, x, y):
    c = gdi32.GetPixel(hdc, x, y)
    if c == -1: return (0,0,0)
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)

def stats():
    hdc = user32.GetDC(0)
    try:
        blue = white = dark = gray = total = 0
        for y in range(Y0, Y1+1, STEP):
            for x in range(X0, X1+1, STEP):
                r, g, b = get_pixel(hdc, x, y)
                total += 1
                # 蓝色（待发送）
                if b > 180 and b > r + 30 and b > g + 15:
                    blue += 1
                # 白色（运行方块）
                elif r > 220 and g > 220 and b > 220:
                    white += 1
                # 深灰/黑（背景）
                elif r < 100 and g < 100 and b < 110:
                    dark += 1
                else:
                    gray += 1
        return blue, white, dark, gray, total
    finally:
        user32.ReleaseDC(0, hdc)

print(f"CodeBuddy 按钮区 ({X0},{Y0})-({X1},{Y1}) · 每秒刷新 · Ctrl+C 停")
print("操作：空闲10s → 打字 → 发送 → 等答完")
print("-" * 80)
print(f"{'时间':<10} {'蓝':<5} {'白':<5} {'深':<5} {'灰':<5} {'总':<5}  推测状态")
print("-" * 80)

while True:
    blue, white, dark, gray, total = stats()
    # 简单推测
    if blue > total * 0.15:
        state = "待发送(蓝)"
    elif white > total * 0.15:
        state = "运行中(白)"
    else:
        state = "空闲(灰/深)"
    ts = time.strftime('%H:%M:%S')
    print(f"{ts:<10} {blue:<5} {white:<5} {dark:<5} {gray:<5} {total:<5}  {state}")
    time.sleep(1)
