import os, re
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

# 收集：被审者 -> [(评审者, 总分, 8维分)]
scores = {p: [] for p in P}
fails = []

for reviewer in P:
    d = os.path.join(R, reviewer, "评审", "规划轮")
    if not os.path.isdir(d): continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"): continue
        target = fn.replace("评审_","").replace(".md","")
        if target not in P: continue
        fp = os.path.join(d, fn)
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            t = f.read()
        # 总分
        m = re.search(r"总分[：:\s]*\**\s*(\d+)\s*/\s*80", t)
        total = int(m.group(1)) if m else None
        # 8 维
        dims = []
        for i, name in enumerate(["兼容","结构","衔接","角色","创意","节奏","文笔","落地"]):
            # 匹配 "1 兼容：**9**/10" 或 "1 兼容：9/10" 等
            pat = rf"{i+1}\s*{name}[^：:\n]*[：:]\s*\**\s*(\d+(?:\.\d+)?)"
            mm = re.search(pat, t)
            dims.append(float(mm.group(1)) if mm else None)
        if total is None and all(x is not None for x in dims):
            total = int(sum(dims))
        scores[target].append({
            "reviewer": reviewer, "total": total, "dims": dims,
            "file": fn,
        })

print("=" * 80)
print(f"{'被审者':12} {'分数(5人)':40} {'均分':>6}")
print("=" * 80)
rank = []
for p in P:
    lst = scores[p]
    totals = [x["total"] for x in lst if x["total"] is not None]
    avg = sum(totals)/len(totals) if totals else 0
    s = " ".join(f"{x['reviewer'][:6]}:{x['total'] if x['total'] else '?'}" for x in lst)
    print(f"{p:12} {s:40} {avg:6.1f}")
    rank.append((p, avg, len(totals)))

print("\n=== 按均分排名 ===")
for i, (p, avg, n) in enumerate(sorted(rank, key=lambda x:-x[1]), 1):
    print(f"  {i}. {p:12} {avg:6.1f}  (来自 {n} 份评审)")

# 检查有没有抽分失败
print("\n=== 抽分失败 ===")
for p in P:
    for x in scores[p]:
        if x["total"] is None:
            print(f"  ✗ {x['reviewer']} 审 {p}: 抽不到总分 ({x['file']})")
        elif any(d is None for d in x["dims"]):
            print(f"  ⚠ {x['reviewer']} 审 {p}: 部分维度没抽到 {x['dims']}")