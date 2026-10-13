# fix_init_slim.py — 精简 00_初始化 依赖（只读梗概 + 项目信息 + 1.6卷纲）
import shutil
from pathlib import Path

ORCH = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = ORCH.read_text(encoding="utf-8")

# 1) 改 _upstream_files 里规划程序的读取列表
OLD = '''        # 7 份规划蓝图（UI 环节0.5 生成）：1.0_总纲 ~ 1.6_卷纲
        for _bp in ("1.0_总纲.md", "1.1_定位与卖点.md", "1.2_故事核心主题.md",
                    "1.3_人物系统.md", "1.4_世界观与设定.md",
                    "1.5_结构与节奏.md", "1.6_卷纲.md"):'''
NEW = '''        # 00_初始化 现在只读：梗概 + 卷纲（其余交给 AI 环节自由拓展）
        for _bp in ("第0步梗概.md", "1.6_卷纲.md"):'''
if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("✔ _upstream_files 读取列表已精简")
elif "现在只读：梗概 + 卷纲" in text:
    print("已改过")
else:
    print("✗ 找不到 _upstream_files 锚点")

# 保存
bak = ORCH.with_suffix(".py.bak_initslim")
if not bak.exists():
    shutil.copy(ORCH, bak)
    print(f"已备份：{bak.name}")
ORCH.write_text(text, encoding="utf-8")
print("已保存")