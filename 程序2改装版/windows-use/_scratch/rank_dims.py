import os, re
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
DIMS = ["兼容","结构","衔接","角色","创意","节奏","文笔","落地"]

# scores[被审者] = {维度: [分1, 分2, ...]}
scores = {p: {d: [] for d in DIMS} for p in P}
totals = {p: [] for p in P}
fails = []

for reviewer in P:
    d = os.path.join(R, reviewer, "评审", "规划轮")
    if not os.path.isdir(d): continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"): continue
        target = fn.replace("评审_","").replace(".md","")
        if target not in P: continue
        with open(os.path.join(d, fn), encoding="utf-8", errors="ignore") as f:
            t = f.read()
        for i, name in enumerate(DIMS):
            # 匹配 "1 兼容：**9**/10" / "1 兼容：9/10" / "1 兼容: 9" 等
            pat = rf"{i+1}\s*{name}[^：:\n]{{0,10}}[：:]\s*\**\s*(\d+(?:\.\d+)?)\s*(?:/\s*10)?"
            m = re.search(pat, t)
            if m:
                scores[target][name].append(float(m.group(1)))
            else:
                fails.append(f"{reviewer}→{target} 缺{name}")
        # 总分
        m = re.search(r"总分[：:\s]*\**\s*(\d+(?:\.\d+)?)\s*/\s*80", t)
        if m: totals[target].append(float(m.group(1)))

print("=" * 100)
print(f"{'选手':11} {'兼容':>5} {'结构':>5} {'衔接':>5} {'角色':>5} {'创意':>5} {'节奏':>5} {'文笔':>5} {'落地':>5} {'总分':>6} {'均分':>6}")
print("=" * 100)
rows = []
for p in P:
    vals = []
    for dim in DIMS:
        lst = scores[p][dim]
        v = sum(lst)/len(lst) if lst else 0
        vals.append(v)
    t_avg = sum(totals[p])/len(totals[p]) if totals[p] else 0
    d_avg = sum(vals)/len(vals) if vals else 0
    print(f"{p:11} " + " ".join(f"{v:5.1f}" for v in vals) + f" {t_avg:6.1f} {d_avg:6.1f}")
    rows.append((p, vals, t_avg, d_avg))

print("\n=== 按总分排名 ===")
for i, (p, vals, t_avg, d_avg) in enumerate(sorted(rows, key=lambda x: -x[2]), 1):
    print(f"  {i}. {p:12} 总分 {t_avg:5.1f}  8维均分 {d_avg:5.1f}")

print("\n=== 逐维度排名 ===")
for j, dim in enumerate(DIMS):
    col = sorted(rows, key=lambda x: -x[1][j])
    line = "  " + dim + ": " + " | ".join(f"{p}({v:.1f})" for p, v, _, _ in col)
    print(line)

print("\n=== 抽分失败 ===")
for x in fails[:20]: print("  ", x)
if len(fails) > 20: print(f"  ... 共 {len(fails)} 条")