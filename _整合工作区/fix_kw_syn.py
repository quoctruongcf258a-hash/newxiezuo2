# fix_kw_syn.py — 内容词只取 → 前面的部分
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''        _desc = (phase_cfg.get("desc") or "").strip()
        if _desc:
            for _part in re.split(r"[+\\u2192/\\u3001\\uff0c,\\uff1b;]+", _desc):
                _p = _part.strip()
                if _p and len(_p) <= 12 and not _p.startswith("输出"):
                    out["内容词"].append(_p)'''

NEW = '''        _desc = (phase_cfg.get("desc") or "").strip()
        if _desc:
            _head = _desc.split("\\u2192")[0].split("->")[0]
            for _part in re.split(r"[+/\\u3001\\uff0c,\\uff1b;]+", _head):
                _p = _part.strip()
                if _p and len(_p) <= 12 and not _p.startswith("输出"):
                    out["内容词"].append(_p)'''

text = TARGET.read_text(encoding="utf-8")

if "split(\"\\u2192\")[0]" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
else:
    bak = TARGET.with_suffix(".py.bak_kwsyn")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已改：内容词只取 → 前面")