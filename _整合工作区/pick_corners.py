import ctypes, time, sys
user32 = ctypes.windll.user32

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_pos():
    p = POINT()
    user32.GetCursorPos(ctypes.byref(p))
    return p.x, p.y

corners = []
names = ["左上角", "右上角", "右下角", "左下角"]

print("=" * 60)
print("四角定位器 · 依次把鼠标移到 4 个角，然后按 Enter 记录")
print("=" * 60)
print()

for n in names:
    print(f"把鼠标移到按钮的【{n}】，然后按 Enter...")
    input()
    x, y = get_pos()
    corners.append((x, y))
    print(f"  已记录 {n}：({x}, {y})")
    print()

print("=" * 60)
print("四角坐标：")
for n, c in zip(names, corners):
    print(f"  {n}：{c}")
print()
print("复制下面这行，填进 watch_region.py：")
print(f"CORNERS = {corners}")
