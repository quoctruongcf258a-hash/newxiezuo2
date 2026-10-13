import time, ctypes
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

X, Y = 555, 564

def get_pixel(x, y):
    hdc = user32.GetDC(0)
    try:
        c = gdi32.GetPixel(hdc, x, y)
        return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF) if c != -1 else (0,0,0)
    finally:
        user32.ReleaseDC(0, hdc)

def get_avg(x, y, r=2):
    tr = tg = tb = n = 0
    for dx in range(-r, r+1):
        for dy in range(-r, r+1):
            pr, pg, pb = get_pixel(x+dx, y+dy)
            tr += pr; tg += pg; tb += pb; n += 1
    return (tr//n, tg//n, tb//n)

print(f"监控豆包 ({X}, {Y}) 3x3 平均色 · 每秒刷新 · Ctrl+C 停")
print("操作：1) 空闲10秒  2) 打字  3) 发送  4) 等答完")
print()
while True:
    r, g, b = get_avg(X, Y, 2)
    print(f"[{time.strftime('%H:%M:%S')}]  RGB=({r:3d},{g:3d},{b:3d})  HEX=#{r:02X}{g:02X}{b:02X}")
    time.sleep(1)
