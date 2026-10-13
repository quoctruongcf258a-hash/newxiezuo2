import os, io
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(R, "资料", "指令", "规划轮终审")
os.makedirs(CMD, exist_ok=True)

A = open(os.path.join(R, "_融合产物", "_待审", "版A.md"), encoding="utf-8").read()
B = open(os.path.join(R, "_融合产物", "_待审", "版B.md"), encoding="utf-8").read()

TPL = """【规划轮 · 终审 · 两版对照】

你是「七人赛马」选手 {me}。

## 任务
两份匿名规划方案（不知道谁写的）：版A、版B。

对 A、B 各出一张 8 维评分卡（每维 0-10），写亮点备注，最后只选一份。

## 8 维
1 兼容 / 2 结构 / 3 衔接 / 4 角色 / 5 创意 / 6 节奏 / 7 文笔 / 8 落地

## 格式（A、B 各一张）
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
致命/严重问题：<无 / 描述>

## 终审结论
【终审结论】
胜出版：<A 或 B>
理由：<100-200字>

## 输出位置
写到：{outdir}\\{me}.md

## 完成后
回一句：「终审完成」

========================================
## 版A 全文
========================================

{A}

========================================
## 版B 全文
========================================

{B}
"""

for me in ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]:
    outdir = os.path.join(R, me, "评审", "规划轮终审")
    txt = TPL.format(me=me, outdir=outdir, A=A, B=B)
    fp = os.path.join(CMD, me + ".txt")
    io.open(fp, "w", encoding="utf-8").write(txt)
    print("OK", me, os.path.getsize(fp)//1024, "KB")
