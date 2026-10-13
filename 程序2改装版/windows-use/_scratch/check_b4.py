import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"

# 第4批分配
B4 = {
    "CodeBuddy": "Doubao",
    "QUEST":     "Doubao",
    "Doubao":    "CodeBuddy",
    "Qianwen":   "Doubao",
    "WorkBuddy": "Doubao",
    "ZCode":     "CodeBuddy",
}

print("=" * 55)
print(f"{'选手':12} {'应审':>10} {'应写文件':>20} {'状态':>6}")
print("=" * 55)

ok = 0
missing = []
for me, opp in B4.items():
    fp = os.path.join(R, me, "评审", "章纲轮", f"评审_{opp}.md")
    if os.path.exists(fp):
        sz = os.path.getsize(fp)
        print(f"{me:12} {opp:>10} {f'评审_{opp}.md':>20} {'✅ '+str(sz)+'B':>6}")
        ok += 1
    else:
        print(f"{me:12} {opp:>10} {f'评审_{opp}.md':>20} {'❌':>6}")
        missing.append((me, opp))

print(f"\n第4批：{ok}/6 完成")
if missing:
    print("缺：")
    for me, opp in missing:
        print(f"  {me} 缺 评审_{opp}.md")
