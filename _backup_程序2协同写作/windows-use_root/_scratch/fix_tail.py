import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

def rep(fp, a, b):
    if not os.path.exists(fp): return
    t = open(fp, encoding="utf-8").read()
    t2 = t.replace(a, b)
    if t2 != t:
        open(fp, "w", encoding="utf-8", newline="\n").write(t2)
        print("改:", fp.replace(R, ""))

# 1. 各选手 A1：融合由 QUEST专属负责 → 融合由融合官专属负责
for p in P:
    rep(os.path.join(R, p, "A1_规划任务书.md"),
        "融合由 QUEST专属负责。", "融合由融合官专属负责。")

# 2. QUEST A4：由你（QUEST）专属
rep(os.path.join(R, "QUEST", "A4_润色任务书.md"),
    "融合由你（QUEST）专属，融合只产新文档不改原文件。", "融合由融合官专属负责。")

# 3. 评委_润色轮：交 QUEST 按 B_融合任务书.md
rep(os.path.join(R, "评委_润色轮_评判提示词.md"),
    "交 QUEST按 `B_融合任务书.md` 分批融合", "交融合官按 `B_融合任务书.md` 分批融合")
rep(os.path.join(R, "评委_润色轮_评判提示词.md"),
    "交 QUEST 按 `B_融合任务书.md` 分批融合", "交融合官按 `B_融合任务书.md` 分批融合")

# 4. 00_总流程说明：7 个 → 6 个 AI（去掉 TRAE）
fp = os.path.join(R, "00_总流程说明.md")
t = open(fp, encoding="utf-8").read()
t2 = t.replace(
    "7 个不同 AI（CodeBuddy / QUEST / Doubao / Qianwen / TRAE / WorkBuddy / ZCode）",
    "6 个不同 AI（CodeBuddy / QUEST / Doubao / Qianwen / WorkBuddy / ZCode）")
t2 = t2.replace("7 选手各读", "6 选手各读")
t2 = t2.replace("7 选手各出", "6 选手各出")
t2 = t2.replace("7 份规划", "6 份规划")
t2 = t2.replace("7 份章纲", "6 份章纲")
t2 = t2.replace("7 份正文", "6 份正文")
t2 = t2.replace("7 份润色稿", "6 份润色稿")
if t2 != t:
    open(fp, "w", encoding="utf-8", newline="\n").write(t2)
    print("改: 00_总流程说明.md")

print("\n=== 剩的（可不改） ===")
for rel in ["评委_润色轮_评判提示词.md","00_总流程说明.md"]:
    fp = os.path.join(R, rel)
    if os.path.exists(fp):
        for i, line in enumerate(open(fp, encoding="utf-8").read().splitlines(), 1):
            if "QUEST" in line and ("融合" in line or "专属" in line):
                print(f"  {rel} L{i}: {line.strip()[:130]}")
