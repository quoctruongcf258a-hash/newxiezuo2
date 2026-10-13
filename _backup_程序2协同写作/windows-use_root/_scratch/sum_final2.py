import os, re
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
print("=" * 70)
print("章纲轮 · 终审汇总")
print("=" * 70)
votes = {"A": [], "B": []}
for p in P:
    fp = os.path.join(R, p, "评审", "章纲轮终审", f"{p}.md")
    if not os.path.exists(fp):
        print(f"  XX {p:12} 未交"); continue
    t = open(fp, encoding="utf-8", errors="ignore").read()
    m = re.search(r"胜出版[：:\s]*\**\s*([AB])", t)
    win = m.group(1) if m else "?"
    totals = re.findall(r"总分[：:\s]*\**\s*(\d+)\s*/\s*80", t)
    ta = totals[0] if len(totals) > 0 else "?"
    tb = totals[1] if len(totals) > 1 else "?"
    if win == "A": votes["A"].append(p)
    if win == "B": votes["B"].append(p)
    print(f"  {p:12}  A={ta:>3}  B={tb:>3}  胜出={win}")
print()
print(f"版A（WorkBuddy 原稿）  {len(votes['A'])} 票  {votes['A']}")
print(f"版B（ZCode 融合总稿） {len(votes['B'])} 票  {votes['B']}")
if len(votes["A"]) > len(votes["B"]):
    print(f"\n胜出：版A")
elif len(votes["B"]) > len(votes["A"]):
    print(f"\n胜出：版B")
else:
    print(f"\n平票 {len(votes['A'])}:{len(votes['B'])}")
