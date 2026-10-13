import os, io, sys, time
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")

R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(R, "资料", "指令", "正文轮终审")
os.makedirs(CMD, exist_ok=True)

# 读两版
A = open(os.path.join(R, "WorkBuddy", "产出", "正文轮", "18-A_桥下之鬼.md"), encoding="utf-8").read()
B = open(os.path.join(R, "_融合产物", "融合_总稿_正文轮.md"), encoding="utf-8").read()

TPL = """【正文轮 · 终审 · 两版对照】

你是「七人赛马」选手。两份匿名 18-A 正文：版A、版B。
对 A、B 各出一张 8 维评分卡，最后只选一份。

## 8 维
1 兼容 / 2 结构 / 3 衔接 / 4 角色 / 5 创意 / 6 节奏 / 7 文笔 / 8 落地

## 正文特有核对
- 字数 3000-3500
- 单段 <=150 字
- 破折号 0
- 情绪刺激点 >=2 处
- 尾钩与章纲一致
- 接缝（开头两句 + 不复述 18 章末）

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

## 终审结论
【终审结论】
胜出版：<A 或 B>
理由：<100-200字>

## 输出位置
写到：{root}\\{{你的名字}}\\评审\\正文轮终审\\{{你的名字}}.md

## 完成后
回一句：「正文终审完成」

========================================
## 版A 全文
========================================
{A}

========================================
## 版B 全文
========================================
{B}
"""

txt = TPL.format(root=R, A=A, B=B)
fp = os.path.join(CMD, "公共.txt")
io.open(fp, "w", encoding="utf-8").write(txt)
print(f"生成: {os.path.getsize(fp)//1024} KB")

# 直接发送
from mix_send import send
print("发送中...")
for ai in ["ZCode", "QUEST", "WorkBuddy", "Qianwen", "CodeBuddy", "Doubao"]:
    print(f"  -> {ai}: " + send(ai, txt))
    time.sleep(4)
print("完成")
