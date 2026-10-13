import os, re
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

B5 = {
    "CodeBuddy": "ZCode",
    "QUEST":     "ZCode",
    "Doubao":    "ZCode",
    "Qianwen":   "ZCode",
    "WorkBuddy": "ZCode",
    "ZCode":     "Doubao",
}

print("=" * 90)
print(f"{'选手':12} {'审对象':>8} {'文件':>10} {'大小':>6} {'8维':>4} {'定位卡':>5} {'结论':>4} {'总评':>6}")
print("=" * 90)

ok = 0
for me, opp in B5.items():
    fp = os.path.join(R, me, "评审", "章纲轮", f"评审_{opp}.md")
    if not os.path.exists(fp):
        print(f"{me:12} {opp:>8} {'缺':>10} {'-':>6} {'-':>4} {'-':>5} {'-':>4} {'❌':>6}")
        continue
    sz = os.path.getsize(fp)
    t = open(fp, encoding="utf-8", errors="ignore").read()
    # 8维分数
    n_dim = len(re.findall(r"[1-8]\s*(?:兼容|结构|衔接|角色|创意|节奏|文笔|落地)[^：:\n]{0,10}[：:]\s*\**\s*\d+", t))
    # 定位卡
    n_card = t.count("【问题定位卡】")
    # 结论
    has_concl = ("是否通过" in t) or ("胜出版" in t) or ("通过" in t and "打回" in t)
    # 总评
    complete = (n_dim >= 8) and (n_card >= 1) and has_concl and (sz > 3000)
    if complete: ok += 1
    print(f"{me:12} {opp:>8} {'OK':>10} {sz:>6} {n_dim:>4} {n_card:>5} {'✅' if has_concl else '❌':>4} {'✅' if complete else '⚠️':>6}")

print(f"\n第5批：{ok}/6 完整")
