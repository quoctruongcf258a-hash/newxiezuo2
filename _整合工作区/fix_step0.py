# fix_step0.py — 重写步骤0的提示词 + 删旧文件
import shutil
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

# ── 1) 删旧 no0tisc.md ──
old = BASE / "prompts" / "步骤0" / "no0tisc.md"
if old.exists():
    bak = old.with_suffix(".md.bak_old")
    if not bak.exists():
        shutil.copy(old, bak)
        print(f"已备份：{bak.name}")
    old.unlink()
    print(f"✔ 删除 {old.name}")
else:
    print("no0tisc.md 不存在")

# 也删 AI指派协作 下的
old2 = BASE / "AI指派协作" / "prompts" / "步骤0" / "no0tisc.md"
if old2.exists():
    old2.unlink()
    print(f"✔ 删除 {old2.relative_to(BASE)}")

# ── 2) 重写故事梗概.md ──
T = BASE / "prompts" / "00_初始化" / "故事梗概.md"
bak = T.with_suffix(".md.bak_new")
if not bak.exists():
    shutil.copy(T, bak)
    print(f"已备份：{bak.name}")

NEW = '''# 任务：步骤0 · 生成故事梗概与建议方向

## 你的角色
你是网文策划。基于用户输入的关键词 / 参考大纲，产出一段故事梗概和几个差异化建议方向，供后续「规划」程序自由拓展。

## 输入材料
- 用户输入（关键词 + 参考大纲）：`{{产物目录}}\\00_初始化\\用户输入.md`
- 项目初始化信息（JSON）：`{{PROJECT_JSON}}`

## 平台约束（必须遵守）
{{平台规则}}

## 任务

### 第一步：读懂用户想要的感觉
用户会给一组关键词（题材、金手指、感情线、性格标签……）和一份可选参考大纲。
这些可能互相矛盾、归类混乱。**不要逐条检查标签是否矛盾**，而是**整体理解用户想要的作品方向**，自行判断：
- 哪些标签是核心，必须保留
- 哪些标签可以降级为支线或前史
- 哪些标签互相冲突，需要取舍或分层

### 第二步：产出 1 份文件

**只生成一份文件**：`第0步梗概.md`

严格按下面结构输出：

```markdown
# 第0步 · 故事梗概与建议方向

## 一、故事梗概
（约 400 字：主角是谁 + 遇到什么 + 想做什么 + 谁阻止 + 大致走向）

## 二、建议方向（4 个）

### 方向 A：<方向名>
- 核心看点：<一句话>
- 走向概要：<两句话>
- 适合读者：<一句话>

### 方向 B：<方向名>
- 核心看点：
- 走向概要：
- 适合读者：

### 方向 C：<方向名>
- 核心看点：
- 走向概要：
- 适合读者：

### 方向 D：<方向名>
- 核心看点：
- 走向概要：
- 适合读者：

## 三、核心关键词
- 题材：<关键词>
- 主角：<关键词>
- 金手指：<关键词>
- 核心冲突：<关键词>
- 风格：<关键词>