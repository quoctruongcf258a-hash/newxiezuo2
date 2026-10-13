import os, io

R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD_DIR = os.path.join(R, "资料", "指令", "融合轮")
os.makedirs(CMD_DIR, exist_ok=True)

P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

def my_out_dir():
    return os.path.join(R, "QUEST", "融合", "规划轮")

TPL = """【规划轮 · 融合 · 批{batch}】

你是融合官 **QUEST**。

## 本批任务
{brief}

## 输入（读以下文件）

### A. 6 家规划原文（同名文件，6 个目录下）
{plan_files}

### B. 6 份评审汇总（每份 = 一家收到的 5 位对手评审）
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\QUEST\\融合\\评审汇总\\对CodeBuddy的评审_5份.md
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\QUEST\\融合\\评审汇总\\对QUEST的评审_5份.md
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\QUEST\\融合\\评审汇总\\对Doubao的评审_5份.md
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\QUEST\\融合\\评审汇总\\对Qianwen的评审_5份.md
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\QUEST\\融合\\评审汇总\\对WorkBuddy的评审_5份.md
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\QUEST\\融合\\评审汇总\\对ZCode的评审_5份.md

## 输出
写到：{outdir}\\{outfile}

## 融合方法（重要）
- **不设主干**：6 家规划各有优劣，逐模块（子主题）分别看 6 家怎么做的
- 每个模块**选最优那份做底**，把其他家亮点当补丁吸收
- 冲突处按 `共享_任务上下文.md` 红线裁决（九尾不离体 / 卡多逃 / 守鹤不全暴走 / 台账+2 / 远处不预警 / 月面只解部分）
- **避免缝合怪**：人物语气、节奏、设定必须统一
- 每份开头「上文衔接」、结尾「本段落点」

## 完成后
回一句：「批{batch}完成」
"""

BATCHES = [
    (1, "融合 6 家的 规划_1_章节切分 + 规划_2_叙事结构 → 融合_1_章节切分与叙事结构.md",
     "规划_1_*.md 和 规划_2_*.md",
     "融合_1_章节切分与叙事结构.md"),
    (2, "融合 6 家的 规划_3_每章核心与主题 + 规划_4_角色戏份 → 融合_2_每章核心与角色戏份.md",
     "规划_3_*.md 和 规划_4_*.md",
     "融合_2_每章核心与角色戏份.md"),
    (3, "融合 6 家的 规划_5_衔接与地牢深化方案 → 融合_3_衔接与地牢深化.md",
     "规划_5_*.md",
     "融合_3_衔接与地牢深化.md"),
    (4, "融合 6 家的 规划_6_风险规避与自检 → 融合_4_风险规避与自检.md",
     "规划_6_*.md",
     "融合_4_风险规避与自检.md"),
]

for b, brief, pfiles, outfile in BATCHES:
    lines = []
    for p in P:
        d = os.path.join(R, p, "产出", "规划轮")
        lines.append(f"- {d}\\{pfiles}")
    plan_str = "\n".join(lines)
    cmd = TPL.format(
        batch=b, brief=brief, plan_files=plan_str,
        outdir=my_out_dir(), outfile=outfile,
    )
    out = os.path.join(CMD_DIR, f"融合_第{b}批.txt")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(cmd)
    print(f"✅ 融合_第{b}批.txt  ({os.path.getsize(out)/1024:.1f} KB)")

# 末步：汇总
FINAL = """【规划轮 · 融合 · 末步 · 汇总】

你是融合官 QUEST。

## 任务
读你自己刚写好的 4 批融合稿：
- QUEST\\融合\\规划轮\\融合_1_章节切分与叙事结构.md
- QUEST\\融合\\规划轮\\融合_2_每章核心与角色戏份.md
- QUEST\\融合\\规划轮\\融合_3_衔接与地牢深化.md
- QUEST\\融合\\规划轮\\融合_4_风险规避与自检.md

## 输出
写一份汇总到：QUEST\\融合\\融合_总稿_规划轮.md

内容结构：
1. 总览（200 字内）
2. 4 批核心结论压缩成一份「规划定稿」
3. **融合取舍说明**：每个模块从哪家摘了主干，吸收了哪家的什么亮点，舍了谁为什么

## 完成后
回一句：「规划轮融合完成，总稿已落盘」
"""
out = os.path.join(CMD_DIR, "融合_末步_汇总.txt")
with io.open(out, "w", encoding="utf-8") as f:
    f.write(FINAL)
print(f"✅ 融合_末步_汇总.txt  ({os.path.getsize(out)/1024:.1f} KB)")

print(f"\n共 5 份，位置: {CMD_DIR}")