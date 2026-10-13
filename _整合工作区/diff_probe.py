import time, ctypes, json
from pathlib import Path
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

CX, CY = 563, 569
R = 40
STEP = 3

def get_pixel(hdc, x, y):
    c = gdi32.GetPixel(hdc, x, y)
    if c == -1: return (0, 0, 0)
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)

def snapshot():
    hdc = user32.GetDC(0)
    try:
        grid = {}
        for dy in range(-R, R+1, STEP):
            for dx in range(-R, R+1, STEP):
                r, g, b = get_pixel(hdc, CX+dx, CY+dy)
                grid[(dx, dy)] = (r, g, b)
        return grid
    finally:
        user32.ReleaseDC(0, hdc)

print(f"差异点探测器 · ({CX}, {CY}) 周围 ±{R}")
print("=" * 60)
print("第 1 步：保持豆包【空闲】10 秒内不要动")
print()

# 采样空闲基线：连续采 5 次取中位数
print("采空闲基线...")
baselines = [snapshot() for _ in range(5)]
keys = list(baselines[0].keys())
baseline = {}
for k in keys:
    vals = [b[k] for b in baselines]
    # 每个通道取中位数
    r = sorted(v[0] for v in vals)[2]
    g = sorted(v[1] for v in vals)[2]
    b = sorted(v[2] for v in vals)[2]
    baseline[k] = (r, g, b)
print(f"空闲基线已记录 {len(baseline)} 个点")
print()

print("=" * 60)
print("第 2 步：给豆包发一个【长任务】（比如写 3000 字），让它运行 30 秒以上")
print("=" * 60)
input("按 Enter 后开始采集【运行中】数据...")

print("采运行中数据（连续 10 秒）...")
running_samples = []
for i in range(10):
    running_samples.append(snapshot())
    time.sleep(1)

# 对每个点，计算运行中 vs 基线的最大差异
print()
print("=" * 60)
print("差异分析：找出在【运行中】和【空闲】差异最大的点")
print("=" * 60)

diff_pts = []
for k in keys:
    base = baseline[k]
    # 运行中每个采样点的最大值和最小值
    rs = [s[k][0] for s in running_samples]
    gs = [s[k][1] for s in running_samples]
    bs = [s[k][2] for s in running_samples]
    # 取运行中代表值（中位数）
    r_med = sorted(rs)[len(rs)//2]
    g_med = sorted(gs)[len(gs)//2]
    b_med = sorted(bs)[len(bs)//2]
    # 与基线的欧氏距离
    d = ((r_med - base[0])**2 + (g_med - base[1])**2 + (b_med - base[2])**2) ** 0.5
    diff_pts.append((d, k, base, (r_med, g_med, b_med)))

diff_pts.sort(reverse=True)

print(f"差异最大的前 15 个点：")
print(f"{'坐标':<14}  {'空闲RGB':<18}  {'运行RGB':<18}  差异")
for d, (dx, dy), base, run in diff_pts[:15]:
    abs_x = CX + dx
    abs_y = CY + dy
    print(f"({abs_x:4d},{abs_y:4d})    {str(base):<18}  {str(run):<18}  {d:.1f}")

# 保存结果
out = Path(r"F:\赛马23环整合工作室\_整合工作区\doubao_diff_pts.json")
out.write_text(json.dumps([
    {"abs": [CX+dx, CY+dy], "base": base, "run": run, "diff": d}
    for d, (dx, dy), base, run in diff_pts[:20]
], ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n已保存前 20 个点：{out}")
