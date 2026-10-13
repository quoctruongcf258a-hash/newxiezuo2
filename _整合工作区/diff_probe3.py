import time, ctypes, json
from pathlib import Path
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

CX, CY = 563, 569
R = 40
STEP = 6

def get_pixel(hdc, x, y):
    c = gdi32.GetPixel(hdc, x, y)
    if c == -1: return (0, 0, 0)
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)

def snapshot():
    hdc = user32.GetDC(0)
    try:
        g = {}
        for dy in range(-R, R+1, STEP):
            for dx in range(-R, R+1, STEP):
                g[(dx, dy)] = get_pixel(hdc, CX+dx, CY+dy)
        return g
    finally:
        user32.ReleaseDC(0, hdc)

print("=" * 60)
print("阶段 1：采空闲基线（5 秒）")
print("现在什么都别动！")
print("=" * 60)
for i in range(5, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

baselines = [snapshot() for _ in range(5)]
keys = list(baselines[0].keys())
baseline = {}
for k in keys:
    vals = [b[k] for b in baselines]
    baseline[k] = (sorted(v[0] for v in vals)[2],
                   sorted(v[1] for v in vals)[2],
                   sorted(v[2] for v in vals)[2])
print(f"  基线已记录 {len(baseline)} 点")
print()

print("=" * 60)
print("阶段 2：现在立刻给豆包发长任务！")
print("采运行中数据（30 秒）")
print("=" * 60)

running_all = []
for i in range(30):
    running_all.append(snapshot())
    time.sleep(1)
    print(f"  已采 {i+1}/30")

print()
print("=" * 60)
print("差异分析")
print("=" * 60)

diff_pts = []
for k in keys:
    base = baseline[k]
    max_d = 0
    max_val = base
    for s in running_all:
        v = s[k]
        d = ((v[0]-base[0])**2 + (v[1]-base[1])**2 + (v[2]-base[2])**2) ** 0.5
        if d > max_d:
            max_d = d
            max_val = v
    diff_pts.append((max_d, k, base, max_val))

diff_pts.sort(reverse=True)

print(f"\n差异最大的前 20 个点：")
print(f"{'绝对坐标':<14}  {'空闲RGB':<18}  {'运行中RGB':<18}  差异")
for d, (dx, dy), base, run in diff_pts[:20]:
    ax, ay = CX+dx, CY+dy
    print(f"({ax:4d},{ay:4d})    {str(base):<18}  {str(run):<18}  {d:.1f}")

out = Path(r"F:\赛马23环整合工作室\_整合工作区\doubao_diff_pts.json")
out.write_text(json.dumps([
    {"abs": [CX+dx, CY+dy], "base": list(base), "run": list(run), "diff": d}
    for d, (dx, dy), base, run in diff_pts[:20]
], ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n已保存：{out}")
