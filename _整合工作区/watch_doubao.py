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

print(f"监控豆包发送按钮 ({X}, {Y}) · Ctrl+C 停")
print("操作：1) 空闲10秒  2) 打字  3) 发送  4) 等答完")
print()
last = None
while True:
    r, g, b = get_pixel(X, Y)
    cur = (r, g, b)
    if cur != last:
        print(f"[{time.strftime('%H:%M:%S')}]  RGB=({r},{g},{b})  HEX=#{r:02X}{g:02X}{b:02X}")
        last = cur
    time.sleep(0.3)
