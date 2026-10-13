# patch_read_init.py — 读取资料里补上 00_初始化 的 7 份规划蓝图
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''    # 首个程序（规划）读 00_初始化 的项目信息
    if program == "规划":
        _info = _root / "00_初始化" / "项目信息.json"
        if _info.exists():
            ups.append(str(_info))
'''

NEW = '''    # 首个程序（规划）读 00_初始化 的项目信息 + 7 份规划蓝图
    if program == "规划":
        _init_dir = _root / "00_初始化"
        _info = _init_dir / "项目信息.json"
        if _info.exists():
            ups.append(str(_info))
        # 7 份规划蓝图（UI 环节0.5 生成）：1.0_总纲 ~ 1.6_卷纲
        for _bp in ("1.0_总纲.md", "1.1_定位与卖点.md", "1.2_故事核心主题.md",
                    "1.3_人物系统.md", "1.4_世界观与设定.md",
                    "1.5_结构与节奏.md", "1.6_卷纲.md"):
            _fp = _init_dir / _bp
            if _fp.exists():
                ups.append(str(_fp))
'''

text = TARGET.read_text(encoding="utf-8")

if "7 份规划蓝图" in text:
    print("已打过补丁")
elif OLD not in text:
    print("找不到锚点")
else:
    bak = TARGET.with_suffix(".py.bak_readinit")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已补上 7 份规划蓝图到读取资料")