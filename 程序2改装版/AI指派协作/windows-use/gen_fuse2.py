import os, io
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(R, "资料", "指令", "章纲轮融合")
os.makedirs(CMD, exist_ok=True)

P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

def paths_for(file_name):
    lines = []
    for p in P:
        lines.append(f"- {R}\\{p}\\产出\\章纲轮\\{file_name}")
    return "\n".join(lines)

REVIEWS = "\n".join(
    f"- {R}\\_融合产物\\章纲轮_评审汇总\\对{p}的评审_5份.md"
    for p in P
)

DIM_TABLE = f"- {R}\\_融合产物\\章纲轮_8维取优来源表.md"

BATCHES = [
    (1, "章纲_0_总纲.md", "融合_章纲_0_总纲.md",
     "融合 6 家的「总纲」（主题/爆点/情绪曲线）"),
    (2, "章纲_1_分章章纲.md", "融合_章纲_1_分章章纲.md",
     "融合 6 家的「分章章纲」（每章16字段轨+交付轨）— 最大的一批，逐章比对取优"),
    (3, "章纲_2_人物表现要点.md", "融合_章纲_2_人物表现要点.md",
     "融合 6 家的「人物表现要点」（陆炎/再不斩/白/卡多/我爱罗）"),
    (4, "章纲_3_衔接设计.md", "融合_章纲_3_衔接设计.md",
     "融合 6 家的「衔接设计」（接18/19/后续沙忍村）"),
    (5, "章纲_4_自评.md", "融合_章纲_4_自评.md",
     "融合 6 家的「自评」+ 对比 8 维取优表"),
]

TPL = """【章纲轮 · 融合 · 批{b}】

你是融合官 **ZCode**。

## 本批任务
{brief}

## 输入（读以下文件）

### A. 6 家的 {fname}（逐条读）
{fpaths}

### B. 6 份评审汇总（每份 = 一家收到的 5 位对手评审）
{reviews}

### C. 8 维取优来源表
{dimtable}

## 输出
写到：{outdir}\\{outfile}

## 融合方法（重要）
- **不设单一主干**：逐模块看 6 家怎么做，每模块选最优做底，其余亮点作补丁
- **8 维取优**：对照 8 维取优来源表，每维度从冠军/亚军那里摘
- 冲突按 `共享_任务上下文.md` 红线裁决
- **避免缝合怪**：人物语气、节奏、设定必须统一
- 每份开头「上文衔接」，结尾「本段落点」

## 完成后
回一句：「章纲轮融合批{b}完成」
"""

for b, fname, outfile, brief in BATCHES:
    txt = TPL.format(
        b=b, brief=brief, fname=fname,
        fpaths=paths_for(fname),
        reviews=REVIEWS,
        dimtable=DIM_TABLE,
        outdir=os.path.join(R, "_融合产物", "章纲轮"),
        outfile=outfile,
    )
    fp = os.path.join(CMD, f"融合_章纲轮_批{b}.txt")
    io.open(fp, "w", encoding="utf-8").write(txt)
    print(f"批{b}: {os.path.getsize(fp)//1024} KB")

# 末步
FIN = f"""【章纲轮 · 融合 · 末步 · 汇总】

你是融合官 **ZCode**。

## 任务
读你刚写的 5 批融合稿：
- {R}\\_融合产物\\章纲轮\\融合_章纲_0_总纲.md
- {R}\\_融合产物\\章纲轮\\融合_章纲_1_分章章纲.md
- {R}\\_融合产物\\章纲轮\\融合_章纲_2_人物表现要点.md
- {R}\\_融合产物\\章纲轮\\融合_章纲_3_衔接设计.md
- {R}\\_融合产物\\章纲轮\\融合_章纲_4_自评.md

## 输出
写一份汇总到：{R}\\_融合产物\\融合_总稿_章纲轮.md

内容结构：
1. 总览（200 字内）
2. 5 批核心结论压缩成一份「章纲定稿」
3. **融合取舍说明**：每个模块从哪家摘了主干，吸收了哪家的什么亮点，舍了谁为什么

## 完成后
回一句：「章纲轮融合完成，总稿已落盘」
"""
fp = os.path.join(CMD, "融合_章纲轮_末步.txt")
io.open(fp, "w", encoding="utf-8").write(FIN)
print(f"末步: {os.path.getsize(fp)//1024} KB")

# 建输出目录
os.makedirs(os.path.join(R, "_融合产物", "章纲轮"), exist_ok=True)
print(f"\n共 6 份，位置: {CMD}")
