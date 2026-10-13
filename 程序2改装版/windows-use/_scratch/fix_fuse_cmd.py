import os, io

CMD_DIR = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马\资料\指令\融合轮"
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

# 每批读哪些具体文件
BATCH_FILES = {
    1: ["规划_1_章节切分.md", "规划_2_叙事结构.md"],
    2: ["规划_3_每章核心与主题.md", "规划_4_角色戏份.md"],
    3: ["规划_5_衔接与地牢深化方案.md"],
    4: ["规划_6_风险规避与自检.md"],
}

for b, files in BATCH_FILES.items():
    fp = os.path.join(CMD_DIR, f"融合_第{b}批.txt")
    with open(fp, "r", encoding="utf-8") as f:
        txt = f.read()
    # 替换通配符段
    lines = []
    for p in P:
        d = os.path.join(R, p, "产出", "规划轮")
        for fn in files:
            lines.append(f"- {d}\\{fn}")
    new_section = "\n".join(lines)
    # 找到旧列表并替换（从 "- C:\...CodeBuddy\产出" 到 "- C:\...ZCode\产出..."）
    import re
    txt2 = re.sub(r"### A\. 6 家规划原文（同名文件，6 个目录下）\n(?:- [^\n]+\n)+",
                  f"### A. 6 家规划原文（12 个文件，逐条读）\n{new_section}\n",
                  txt)
    with io.open(fp, "w", encoding="utf-8") as f:
        f.write(txt2)
    print(f"✅ 修正 融合_第{b}批.txt")

# 建输出目录
outdir = os.path.join(R, "QUEST", "融合", "规划轮")
os.makedirs(outdir, exist_ok=True)
print(f"\n✅ 输出目录已建: {outdir}")