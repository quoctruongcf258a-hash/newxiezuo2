# fix_format.py — format_note 里规划环节按 desc 拆字段
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''    key = phase_cfg.get("key", "")
    if program == "规划":
        return "输出结构化条目（`字段名：内容`），像一份可直接归档的设定表或清单。"
'''

NEW = '''    key = phase_cfg.get("key", "")
    if program == "规划":
        # 从 desc 拆出字段模板
        _desc = (phase_cfg.get("desc") or "").strip()
        _head = _desc
        for _sep in ("→", "->", "=>"):
            if _sep in _head:
                _head = _head.split(_sep)[0]
                break
        _fields = []
        import re as _re
        for _p in _re.split(r"[+/、，,；;]+", _head):
            _p = _p.strip()
            if _p and len(_p) <= 12 and not _p.startswith("输出"):
                _fields.append(_p)
        if _fields:
            _lines = "\\n".join(f"  {f}：" for f in _fields)
            return ("严格按下面字段输出，一行一个字段，不要增减：\\n"
                    + _lines
                    + "\\n  （补充说明：如本环节有其他必要信息，可在最后另起一节）")
        return "输出结构化条目（`字段名：内容`），像一份可直接归档的设定表或清单。"
'''

text = TARGET.read_text(encoding="utf-8")

if "严格按下面字段输出" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
else:
    bak = TARGET.with_suffix(".py.bak_format")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已改 format_note")