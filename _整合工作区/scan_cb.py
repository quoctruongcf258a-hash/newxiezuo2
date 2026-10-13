import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import _get_pixel

# 扫描 (663, 988) 周围 ±10，看实际按钮在哪
print("扫描 (663, 988) 周围 ±10：")
for dy in range(-10, 11, 2):
    row = []
    for dx in range(-10, 11, 2):
        r, g, b = _get_pixel(663+dx, 988+dy)
        if r > 220 and g > 220 and b > 220: row.append("W")
        elif b > 200 and b > r + 30: row.append("U")
        elif r < 130 and g < 130 and b < 130: row.append(".")
        else: row.append("-")
    print("".join(row))
print()
print("中心点颜色：", _get_pixel(663, 988))
