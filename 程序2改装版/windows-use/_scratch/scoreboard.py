import os, re
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
DIMS = ["兼容","结构","衔接","角色","创意","节奏","文笔","落地"]

def scan(round_name):
    scores = {p: {d: [] for d in DIMS} for p in P}
    totals = {p: [] for p in P}
    for reviewer in P:
        d = os.path.join(R, reviewer, "评审", round_name)
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
    return scores, totals

def show(round_name):
    print(f"\n========== {round_name} ==========")
    scores, totals = scan(round_name)
    print(f"{'选手':11} " + " ".join(f"{d:>5}" for d in DIMS) + f" {'总分':>6} {'均分':>6} {'份数':>4}")
    rows = []
    for p in P:
        vals = []
        for dim in DIMS:
            lst = scores[p][dim]
            vals.append(sum(lst)/len(lst) if lst else 0)
        t_avg = sum(totals[p])/len(totals[p]) if totals[p] else 0
        d_avg = sum(vals)/len(vals) if vals else 0
        n = len(totals[p])
        print(f"{p:11} " + " ".join(f"{v:5.1f}" for v in vals) + f" {t_avg:6.1f} {d_avg:6.1f} {n:>4}")
        rows.append((p, t_avg))
    print("\n排名：")
    for i, (p, s) in enumerate(sorted(rows, key=lambda x:-x[1]), 1):
        print(f"  {i}. {p:12} {s:5.1f}")

show("规划轮")
show("章纲轮")
