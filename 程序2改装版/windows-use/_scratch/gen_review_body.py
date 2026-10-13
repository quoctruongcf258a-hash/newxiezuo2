import os, io
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(R, "资料", "指令", "正文轮评审")
os.makedirs(CMD, exist_ok=True)

AIS = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

def read_body(name):
    d = os.path.join(R, name, "产出", "正文轮")
    if not os.path.isdir(d): return ""
    chunks = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"): continue
        chunks.append(f"\n\n--- {name}/{fn} ---\n" + open(os.path.join(d, fn), encoding="utf-8").read())
    return "".join(chunks)

TPL = """【正文轮 · 互审 · 第{b}批】

你是「七人赛马」选手 **{me}**。本批你要评审 **{opp}** 的正文。

## 评审标准
1. 8 维打分（每维 0-10）：兼容 / 结构 / 衔接 / 角色 / 创意 / 节奏 / 文笔 / 落地
2. 每维写备注（好在哪 / 有什么问题）
3. ≥3 张问题定位卡
4. 1-3 条亮点备注
5. 结论：通过 / 打回（踩红线=打回）
6. 4 镜交叉：适配人群 / 原著时间线 / 人物特点 / 自洽

## 正文特有核对
- 字数 3000-3500（18-A）
- 单段 ≤150 字
- 破折号 0
- 情绪刺激点 ≥2 处
- 尾钩与章纲一致
- 接缝（开头两句 + 不复述 18 章末）

## 输出位置
写到：{root}\\{me}\\评审\\正文轮\\评审_{opp}.md

## 报告结构
【8维评分卡 · {opp}】
1 兼容：__/10  备注：
2 结构：__/10  备注：
3 衔接：__/10  备注：
4 角色：__/10  备注：
5 创意：__/10  备注：
6 节奏：__/10  备注：
7 文笔：__/10  备注：
8 落地：__/10  备注：
总分：__/80
亮点备注：<1-3条>
致命/严重问题：<无/描述>
是否通过：<通过/打回>

【问题定位卡】×≥3
- 位置：
- 问题类型：
- 具体描述：
- 严重程度：<致命/严重/一般/轻微>
- 修改建议：

【正文特有核对】
- 字数：
- 段落：
- 破折号：
- 情绪刺激点：
- 尾钩：

## 完成后
回一句：「{me} 第{b}批完成」

## {opp} 的正文全文

{body}
"""

count = 0
for me in AIS:
    others = [a for a in AIS if a != me]
    for b, opp in enumerate(others, 1):
        body = read_body(opp)
        txt = TPL.format(me=me, b=b, opp=opp, root=R, body=body)
        fp = os.path.join(CMD, f"{me}_第{b}批.txt")
        io.open(fp, "w", encoding="utf-8").write(txt)
        kb = os.path.getsize(fp) // 1024
        print(f"{me}_第{b}批.txt  ({kb} KB)  → 审 {opp}")
        count += 1

print(f"\n共 {count} 份，位置: {CMD}")
