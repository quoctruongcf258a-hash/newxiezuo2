import os, io, re
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(R, "资料", "指令", "正文轮融合")
os.makedirs(CMD, exist_ok=True)

AIS = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

# 1. 打包评审汇总
OUT1 = os.path.join(R, "_融合产物", "正文轮_评审汇总")
os.makedirs(OUT1, exist_ok=True)
for target in AIS:
    chunks = []
    for reviewer in AIS:
        if reviewer == target: continue
        fp = os.path.join(R, reviewer, "评审", "正文轮", f"评审_{target}.md")
        if not os.path.exists(fp): continue
        t = open(fp, encoding="utf-8", errors="ignore").read()
        chunks.append(f"\n\n===== 来自 {reviewer} 的评审 =====\n\n{t}")
    out = os.path.join(OUT1, f"对{target}的评审_5份.md")
    io.open(out, "w", encoding="utf-8").write(f"# 对 {target} 正文的 5 份评审汇总\n" + "".join(chunks))
    print(f"OK 对{target}的评审_5份.md  ({os.path.getsize(out)//1024} KB)")

# 2. 生成 8 维取优表
DIMS = ["兼容","结构","衔接","角色","创意","节奏","文笔","落地"]
scores = {p: {d: [] for d in DIMS} for p in AIS}
totals = {p: [] for p in AIS}
for reviewer in AIS:
    d = os.path.join(R, reviewer, "评审", "正文轮")
    if not os.path.isdir(d): continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"): continue
        target = fn.replace("评审_","").replace(".md","")
        if target not in AIS: continue
        t = open(os.path.join(d, fn), encoding="utf-8", errors="ignore").read()
        for i, name in enumerate(DIMS):
            pat = rf"{i+1}\s*{name}[^：:\n]{{0,10}}[：:]\s*\**\s*(\d+(?:\.\d+)?)"
            m = re.search(pat, t)
            if m: scores[target][name].append(float(m.group(1)))
        m = re.search(r"总分[：:\s]*\**\s*(\d+(?:\.\d+)?)\s*/\s*80", t)
        if m: totals[target].append(float(m.group(1)))

table = os.path.join(R, "_融合产物", "正文轮_8维取优来源表.md")
with io.open(table, "w", encoding="utf-8") as f:
    f.write("# 正文轮  8维取优来源表\n\n| 选手 | 总分 |\n|---|---|\n")
    rows = []
    for p in AIS:
        avg = sum(totals[p])/len(totals[p]) if totals[p] else 0
        rows.append((p, avg))
    for i, (p, s) in enumerate(sorted(rows, key=lambda x:-x[1]), 1):
        f.write(f"| {i} | {p} | {s:.1f} |\n")
print(f"OK 8维取优表: {table}")

# 3. 生成融合指令
body_paths = "\n".join([f"- {R}\\{ai}\\产出\\正文轮\\18-A_桥下之鬼.md" for ai in AIS])
review_paths = "\n".join([f"- {OUT1}\\对{ai}的评审_5份.md" for ai in AIS])

b1 = f"""【正文轮  融合  批1：前半段】

你是融合官 ZCode。融合 6 家 18-A 正文的【前半段】（约 2000-2500 字，从开头到"下桥墩探查/汇合后的第一个转场"）。

## 输入
### 6 家正文
{body_paths}

### 6 份评审汇总
{review_paths}

### 8 维取优表
{table}

## 输出
写到：{R}\\_融合产物\\正文轮\\融合_正文_前半段.md

## 融合方法
- 逐段（开头/阿松求救/决策/汇合）分别看 6 家，每段选最优做底
- 其他家亮点作补丁
- 冲突按红线裁决，避免缝合怪
- 保持文风统一

## 完成后
回「批1完成」
"""

b2 = f"""【正文轮  融合  批2：后半段】

你是融合官 ZCode。融合 6 家 18-A 正文的【后半段】（约 2000-2500 字，从下桥墩探查到章末钩）。

## 输入
（同批1，重新读一遍）
{body_paths}
{review_paths}

## 输出
写到：{R}\\_融合产物\\正文轮\\融合_正文_后半段.md

## 完成后
回「批2完成」
"""

fin = f"""【正文轮  融合  末步】

读以下两段：
- {R}\\_融合产物\\正文轮\\融合_正文_前半段.md
- {R}\\_融合产物\\正文轮\\融合_正文_后半段.md

组装成完整融合稿，写到：{R}\\_融合产物\\融合_总稿_正文轮.md

要求：
1. 全文 3000-3500 字
2. 统一文风、人物语气
3. 末尾附「融合取舍说明」
4. 完成后回「正文轮融合完成」
"""

for name, txt in [("融合_正文轮_批1.txt", b1), ("融合_正文轮_批2.txt", b2), ("融合_正文轮_末步.txt", fin)]:
    fp = os.path.join(CMD, name)
    io.open(fp, "w", encoding="utf-8").write(txt)
    print(f"OK {name} ({os.path.getsize(fp)//1024} KB)")

print(f"\n位置: {CMD}")
