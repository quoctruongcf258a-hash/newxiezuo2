# use_fields.py — format_note 优先读 phase_cfg["fields"]
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''    key = phase_cfg.get("key", "")
    if program == "规划":
        # 人物设计：多人多文件
'''

NEW = '''    key = phase_cfg.get("key", "")
    if program == "规划":
        # 优先用 phase_cfg 里的 fields 字段（结构化字段列表）
        _fields = phase_cfg.get("fields") or []
        if _fields:
            _lines = "\\n".join(f"  {f}：" for f in _fields)
            return ("严格按下面字段输出，一行一个字段，不要增减：\\n"
                    + _lines
                    + "\\n  （补充说明：如本环节有其他必要信息，可在最后另起一节）")
        # 人物设计：多人多文件
'''

text = TARGET.read_text(encoding="utf-8")

if "优先用 phase_cfg 里的 fields" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
else:
    bak = TARGET.with_suffix(".py.bak_usefields")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ format_note 已优先读 fields")