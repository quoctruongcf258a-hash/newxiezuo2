import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, re
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
DIMS = ["兼容","结构","衔接","角色","创意","节奏","文笔","落地"]

scores = {p: {d: [] for d in DIMS} for p in P}
totals = {p: [] for p in P}

for reviewer in P:
    d = os.path.join(R, reviewer, "评审", "章纲轮")
    if not os.path.isdir(d): continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"): continue
        target = fn.replace("评审_","").replace(".md","")
        if target not in P: continue
        t = open(os.path.join(d, fn), encoding="utf-8", errors="ignore").read()
        for i, name in enumerate(DIMS):
            pat = rf"{i+1}\s*{name}[^：:\n]{{0,10}}[：:]\s*\**\s*(\d+(?:\.\d+)?)"
            m = re.search(pat, t)
            if m: scores[target][name].append(float(m.group(1)))
        m = re.search(r"总分[：:\s]*\**\s*(\d+(?:\.\d+)?)\s*/\s*80", t)
        if m: totals[target].append(float(m.group(1)))

print("=" * 100)
print(f"{'选手':12} " + " ".join(f"{d:>5}" for d in DIMS) + f" {'总分':>6} {'份数':>4}")
print("=" * 100)
rows = []
for p in P:
    vals = []
    for dim in DIMS:
        lst = scores[p][dim]
        vals.append(sum(lst)/len(lst) if lst else 0)
    t_avg = sum(totals[p])/len(totals[p]) if totals[p] else 0
    print(f"{p:12} " + " ".join(f"{v:5.1f}" for v in vals) + f" {t_avg:6.1f} {len(totals[p]):>4}")
    rows.append((p, vals, t_avg))

print("\n=== 按总分排名 ===")
for i, (p, vals, t_avg) in enumerate(sorted(rows, key=lambda x:-x[2]), 1):
    print(f"  {i}. {p:12} {t_avg:5.1f}")

print("\n=== 逐维度冠军 ===")
for j, dim in enumerate(DIMS):
    col = sorted(rows, key=lambda x:-x[1][j])
    print(f"  {dim}: " + "  ".join(f"{p}({vs[j]:.1f})" for p, vs, _ in col[:3]))

# 存表
OUT = os.path.join(R, "_融合产物", "章纲轮_8维取优来源表.md")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# 章纲轮 · 8维取优来源表\n\n")
    f.write("| 名次 | 选手 | 总分 |\n|---|---|---|\n")
    for i, (p, vals, t_avg) in enumerate(sorted(rows, key=lambda x:-x[2]), 1):
        f.write(f"| {i} | {p} | {t_avg:.1f} |\n")
    f.write("\n## 逐维度冠军\n\n")
    for j, dim in enumerate(DIMS):
        col = sorted(rows, key=lambda x:-x[1][j])
        f.write(f"- {dim}: " + " / ".join(f"{p}({vs[j]:.1f})" for p, vs, _ in col[:3]) + "\n")
print(f"\n已存: {OUT}")

