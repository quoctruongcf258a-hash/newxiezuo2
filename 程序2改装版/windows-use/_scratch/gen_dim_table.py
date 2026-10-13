import os, io
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
OUT = os.path.join(R, "_融合产物", "8维取优来源表.md")

content = """# 8 维取优来源表（规划轮 · 30 份互审聚合）

> 数据源：6 家 × 5 位对手的 8 维打分，均分如下。

## 逐维度取优来源

| 维度 | 冠军 | 亚军 | 取用建议 |
|---|---|---|---|
| 1 兼容 | WorkBuddy 9.0 | Qianwen/ZCode 8.4 | 红线处置直接取 WorkBuddy |
| 2 结构 | WorkBuddy 8.8 | Qianwen/ZCode 8.6 | 章节骨架取 WorkBuddy；Qianwen/ZCode 作备选 |
| 3 衔接 | WorkBuddy 9.0 | Qianwen 8.4 | 接 18/19 方案取 WorkBuddy |
| 4 角色 | WorkBuddy 9.0 | ZCode 8.6 | 人物戏份分配取 WorkBuddy |
| 5 创意 | WorkBuddy 9.0 | Qianwen 8.6 | 反转/鬼线巧思取 WorkBuddy；Doubao 的"主动反转"可参考 |
| 6 节奏 | ZCode 8.2 | Qianwen 8.0 | 张弛设计取 ZCode |
| 7 文笔 | Qianwen 8.4（并列 WorkBuddy） | ZCode 8.2 | 机检纪律/禁词表取 Qianwen |
| 8 落地 | WorkBuddy 8.6 | ZCode 8.4 | 可执行性取 WorkBuddy |

## 总分排名

| 名次 | 选手 | 总分 | 定位 |
|---|---|---|---|
| 1 | WorkBuddy | 69.4 | 综合最强，主骨架 |
| 2 | ZCode | 68.6 | 节奏第一，衔接/落地强 |
| 3 | Qianwen | 68.4 | 文笔第一，全面均衡 |
| 4 | QUEST | 61.8 | 中游，衔接短板 |
| 5 | Doubao | 54.2 | 创意可摘 |
| 6 | CodeBuddy | 47.0 | 全线偏弱，仅参考 |

## 融合建议

1. 主干取 **WorkBuddy**（7 维冠军），但**节奏部分取 ZCode**（补 WorkBuddy 节奏 7.6 的短板）
2. 文风机检纪律取 **Qianwen**（禁词表、弹窗白名单、接缝冻结区）
3. 创意补丁：**Doubao** 的「主动性反转」值得吸收，**CodeBuddy** 的「单章只记一次 +2 的记账简洁」可参考
4. 不取：CodeBuddy 的「单章 4500-5500 越硬指标 5000」、QUEST 的「接 19 模型矛盾」
"""

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ 已写:", OUT)