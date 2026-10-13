import os, io

R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(R, "资料", "指令", "融合轮")
os.makedirs(CMD, exist_ok=True)

# 批3
b3 = """【规划轮 · 融合 · 批3】

你是融合官 **ZCode**。

## 已完成（读一下当上下文）
- _融合产物\\规划轮\\融合_1_章节切分与叙事结构.md（批1已写）
- _融合产物\\规划轮\\融合_2_每章核心与角色戏份.md（批2已写）

## 本批任务
融合 6 家的 `规划_5_衔接与地牢深化方案.md` → 写出批3

## 输入（读以下文件）

### A. 6 家的 规划_5（逐条读）
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\CodeBuddy\\产出\\规划轮\\规划_5_衔接与地牢深化方案.md
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\QUEST\\产出\\规划轮\\规划_5_衔接与地牢深化方案.md
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\Doubao\\产出\\规划轮\\规划_5_衔接与地牢深化方案.md
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\Qianwen\\产出\\规划轮\\规划_5_衔接与地牢深化方案.md
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\WorkBuddy\\产出\\规划轮\\规划_5_衔接与地牢深化方案.md
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\ZCode\\产出\\规划轮\\规划_5_衔接与地牢深化方案.md

### B. 6 份评审汇总（每份 = 一家收到的 5 位对手评审）
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\_融合产物\\评审汇总\\对CodeBuddy的评审_5份.md
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\_融合产物\\评审汇总\\对QUEST的评审_5份.md
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\_融合产物\\评审汇总\\对Doubao的评审_5份.md
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\_融合产物\\评审汇总\\对Qianwen的评审_5份.md
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\_融合产物\\评审汇总\\对WorkBuddy的评审_5份.md
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\_融合产物\\评审汇总\\对ZCode的评审_5份.md

## 输出
写到：C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\_融合产物\\规划轮\\融合_3_衔接与地牢深化.md

## 融合方法
- 不设单一主干，逐模块看 6 家怎么做，每模块选最优做底，其余亮点作补丁
- 冲突按 `共享_任务上下文.md` 红线裁决
- 每份开头「上文衔接」，结尾「本段落点」

## 完成后
回一句：「批3完成」
"""

# 批4
b4 = """【规划轮 · 融合 · 批4】

你是融合官 **ZCode**。

## 已完成
- _融合产物\\规划轮\\融合_1_章节切分与叙事结构.md
- _融合产物\\规划轮\\融合_2_每章核心与角色戏份.md
- _融合产物\\规划轮\\融合_3_衔接与地牢深化.md（刚写完）

## 本批任务
融合 6 家的 `规划_6_风险规避与自检.md` → 写出批4

## 输入（读以下文件）

### A. 6 家的 规划_6（逐条读）
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\CodeBuddy\\产出\\规划轮\\规划_6_风险规避与自检.md
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\QUEST\\产出\\规划轮\\规划_6_风险规避与自检.md
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\Doubao\\产出\\规划轮\\规划_6_风险规避与自检.md
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\Qianwen\\产出\\规划轮\\规划_6_风险规避与自检.md
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\WorkBuddy\\产出\\规划轮\\规划_6_风险规避与自检.md
- C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\ZCode\\产出\\规划轮\\规划_6_风险规避与自检.md

### B. 6 份评审汇总
（同上路径，见批3）

## 输出
写到：C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\_融合产物\\规划轮\\融合_4_风险规避与自检.md

## 完成后
回一句：「批4完成」
"""

# 末步
fin = """【规划轮 · 融合 · 末步 · 汇总】

你是融合官 **ZCode**。

## 任务
读你自己刚写好的 4 批融合稿：
- _融合产物\\规划轮\\融合_1_章节切分与叙事结构.md
- _融合产物\\规划轮\\融合_2_每章核心与角色戏份.md
- _融合产物\\规划轮\\融合_3_衔接与地牢深化.md
- _融合产物\\规划轮\\融合_4_风险规避与自检.md

## 输出
写一份汇总到：C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\_融合产物\\融合_总稿_规划轮.md

内容结构：
1. 总览（200 字内）
2. 4 批核心结论压缩成一份「规划定稿」
3. **融合取舍说明**：每个模块从哪家摘了主干，吸收了哪家的什么亮点，舍了谁为什么

## 完成后
回一句：「规划轮融合完成，总稿已落盘」
"""

for name, content in [("融合_ZCode_批3.txt", b3), ("融合_ZCode_批4.txt", b4), ("融合_ZCode_末步.txt", fin)]:
    fp = os.path.join(CMD, name)
    with io.open(fp, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ {name}  ({os.path.getsize(fp)/1024:.1f} KB)")