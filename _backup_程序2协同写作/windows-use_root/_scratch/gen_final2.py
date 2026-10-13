import os, io
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(R, "资料", "指令", "章纲轮终审")
os.makedirs(CMD, exist_ok=True)

# 版A：WorkBuddy 章纲（合并）
d = os.path.join(R, "WorkBuddy", "产出", "章纲轮")
chunks = []
for fn in sorted(os.listdir(d)):
    if not fn.endswith(".md"): continue
    if "总稿" in fn: continue
    chunks.append(f"\n\n===== {fn} =====\n\n" + open(os.path.join(d, fn), encoding="utf-8").read())
A = "".join(chunks)

# 版B：融合总稿
B = open(os.path.join(R, "_融合产物", "融合_总稿_章纲轮.md"), encoding="utf-8").read()

TPL = """【章纲轮 · 终审 · 两版对照】

你是「七人赛马」选手。两份匿名章纲：版A、版B。
对 A、B **各出一张 8 维评分卡**，最后**只选一份**。

## 8 维
1 兼容 / 2 结构 / 3 衔接 / 4 角色 / 5 创意 / 6 节奏 / 7 文笔 / 8 落地

## 章纲特有核对
- 16 字段齐全（1.目标~16.钩子类型）
- 章节类型判定 + 模板正确
- 通用 6 要素：断章钩/代价/未闭合问题/微兑现/情绪刺激/钩型不重复
- 冲突值：常规≥8、峰值≥16
- Strand：主线 55-65% / 情感 20-30% / 世界观 10-20%

## 评分卡格式（A、B 各一张）
【8维评分卡 · 版X】
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

【章纲特有核对（A、B 各一次）】
- 16 字段：
- 章节类型：
- 6 要素：
- 冲突值：
- Strand：

## 终审结论
【终审结论】
胜出版：<A 或 B>
理由：<100-200字>

## 输出位置
写到你自己文件夹：
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\{{你的名字}}\\评审\\章纲轮终审\\{{你的名字}}.md
（例：CodeBuddy 写到 CodeBuddy\\评审\\章纲轮终审\\CodeBuddy.md）

## 完成后
回一句：「章纲终审完成」

========================================
## 版A 全文
========================================
{A}

========================================
## 版B 全文
========================================
{B}
"""

txt = TPL.format(A=A, B=B)
fp = os.path.join(CMD, "公共.txt")
io.open(fp, "w", encoding="utf-8").write(txt)
print(f"OK  版A={len(A)//1024}KB  版B={len(B)//1024}KB  合计={len(txt)//1024}KB")
print(f"写到: {fp}")
