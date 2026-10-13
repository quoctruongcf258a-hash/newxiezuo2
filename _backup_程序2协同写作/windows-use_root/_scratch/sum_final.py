import os, re
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

print("=" * 70)
print(f"{'选手':12} {'A总分':>7} {'B总分':>7} {'胜出':>6}")
print("=" * 70)

votes = {"A": 0, "B": 0}
for p in P:
    fp = os.path.join(R, p, "评审", "规划轮终审", p + ".md")
    if not os.path.exists(fp):
        print(f"{p:12}  还没交")
        continue
    t = open(fp, encoding="utf-8", errors="ignore").read()
    totals = re.findall(r"总分[：:]\s*\**\s*(\d+)\s*/\s*80", t)
    ta = totals[0] if len(totals) > 0 else "?"
    tb = totals[1] if len(totals) > 1 else "?"
    m = re.search(r"胜出版[：:\s]*\**\s*([AB])", t)
    win = m.group(1) if m else "?"
    if win == "A": votes["A"] += 1
    if win == "B": votes["B"] += 1
    print(f"{p:12} {str(ta):>7} {str(tb):>7} {win:>6}")

print("\n=== 票数 ===")
print(f"  版A: {votes['A']} 票")
print(f"  版B: {votes['B']} 票")
if votes["A"] > votes["B"]:
    print(f"  胜出: 版A")
elif votes["B"] > votes["A"]:
    print(f"  胜出: 版B")
else:
    print(f"  平票 {votes['A']}:{votes['B']} → 进第2轮")
