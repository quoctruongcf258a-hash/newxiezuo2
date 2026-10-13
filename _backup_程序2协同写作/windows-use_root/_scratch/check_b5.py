import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"

B5 = {
    "CodeBuddy": "ZCode",
    "QUEST":     "ZCode",
    "Doubao":    "ZCode",
    "Qianwen":   "ZCode",
    "WorkBuddy": "ZCode",
    "ZCode":     "Doubao",
}

ok = 0
missing = []
print("=" * 55)
for me, opp in B5.items():
    fp = os.path.join(R, me, "评审", "章纲轮", f"评审_{opp}.md")
    if os.path.exists(fp):
        print(f"{me:12} → {opp:10}  ✅ {os.path.getsize(fp)} B")
        ok += 1
    else:
        print(f"{me:12} → {opp:10}  ❌ 缺")
        missing.append((me, opp))

print(f"\n第5批：{ok}/6 完成")
if missing:
    print("缺：")
    for me, opp in missing:
        print(f"  {me} 缺 评审_{opp}.md")
