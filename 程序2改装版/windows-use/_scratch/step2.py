import os, re, io, shutil

R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

# 1. ZCode 建 B_融合任务书.md
ZCODE_B = os.path.join(R, "ZCode", "B_融合任务书.md")
BAK_B = r"C:\Users\Administrator\Desktop\新书\火影忍者\_七人赛马备份_融合改名前\B_融合任务书.md"
if os.path.exists(BAK_B):
    t = open(BAK_B, encoding="utf-8").read()
    t = t.replace("（QUEST：QUEST = 唯一融合官）", "（ZCode = 唯一融合官）")
    t = t.replace('你是"七人赛马"的**唯一融合官**。你同时是第2号参赛选手', '你是"七人赛马"的**唯一融合官**。你同时是参赛选手')
    t = t.replace("`QUEST/融合/`", "`_融合产物/`")
    t = t.replace("QUEST/融合/", "_融合产物/")
    t = t.replace("融合官（QUEST）", "融合官")
    open(ZCODE_B, "w", encoding="utf-8", newline="\n").write(t)
    print("✅ 建 ZCode\\B_融合任务书.md")

# 2. 所有选手 A2/A3/A4 + 正文轮提示词：QUEST/融合/ 路径 → _融合产物/
for p in P:
    for fn in ["A2_章纲任务书.md","A3_正文任务书.md","A4_润色任务书.md","正文轮任务提示词.txt"]:
        fp = os.path.join(R, p, fn)
        if not os.path.exists(fp): continue
        t = open(fp, encoding="utf-8").read()
        t2 = t
        t2 = t2.replace("QUEST/融合/", "_融合产物/")
        t2 = t2.replace("QUEST\\\\融合\\\\", "_融合产物\\\\")
        t2 = t2.replace("七人赛马\\QUEST\\融合\\", "七人赛马\\_融合产物\\")
        t2 = t2.replace("融合由 QUEST专属负责", "融合由融合官专属负责")
        t2 = t2.replace("融合由 QUEST专属", "融合由融合官专属")
        if t2 != t:
            open(fp, "w", encoding="utf-8", newline="\n").write(t2)
            print(f"改路径: {p}\\{fn}")

# 3. 删其他选手 00_你的输出位置.md 里"融合产出"那行
for p in P:
    if p == "ZCode": continue
    fp = os.path.join(R, p, "00_你的输出位置.md")
    if not os.path.exists(fp): continue
    t = open(fp, encoding="utf-8").read()
    t2 = re.sub(r"\| 融合产出（仅融合官）[^\n]*\n", "", t)
    if t2 != t:
        open(fp, "w", encoding="utf-8", newline="\n").write(t2)
        print(f"删融合行: {p}\\00_你的输出位置.md")

# 4. 融合轮指令 → ZCode
CMD_DIR = os.path.join(R, "资料", "指令", "融合轮")
for fn in sorted(os.listdir(CMD_DIR)):
    if not fn.endswith(".txt"): continue
    fp = os.path.join(CMD_DIR, fn)
    t = open(fp, encoding="utf-8").read()
    t2 = t.replace("你是融合官 **QUEST**", "你是融合官 **ZCode**")
    t2 = t2.replace("你是融合官 QUEST", "你是融合官 ZCode")
    t2 = t2.replace("七人赛马\\QUEST\\融合\\", "七人赛马\\_融合产物\\")
    t2 = t2.replace("七人赛马\\QUEST\\融合\\评审汇总\\", "七人赛马\\_融合产物\\评审汇总\\")
    t2 = t2.replace("七人赛马\\QUEST\\融合\\规划轮\\", "七人赛马\\_融合产物\\规划轮\\")
    if t2 != t:
        open(fp, "w", encoding="utf-8", newline="\n").write(t2)
        print(f"改指令: {fn}")

# 5. 资料库统一提示词 → 路径
LIB = os.path.join(R, "资料", "资料库")
if os.path.isdir(LIB):
    for fn in sorted(os.listdir(LIB)):
        if not fn.endswith(".md"): continue
        fp = os.path.join(LIB, fn)
        t = open(fp, encoding="utf-8").read()
        t2 = t.replace("QUEST/融合/", "_融合产物/")
        t2 = t2.replace("上轮 QUEST 融合出的", "上轮融合官融合出的")
        t2 = t2.replace("由 QUEST 产出", "由融合官产出")
        if t2 != t:
            open(fp, "w", encoding="utf-8", newline="\n").write(t2)
            print(f"改资料库: {fn}")

print("\n第二步完成")