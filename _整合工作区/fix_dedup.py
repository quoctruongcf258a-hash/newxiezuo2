# fix_dedup.py — keywords_for_phase 返回前去重（保持顺序）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''    if program == "质检":
        for n in phase_cfg.get("qcSecs") or []:
            for s in (cfg.get("qcStandard") or {}).get("sections") or []:
                if str(s.get("n")) == str(n):
                    out["内容词"] += list(s.get("items") or [])

    return out
'''

NEW = '''    if program == "质检":
        for n in phase_cfg.get("qcSecs") or []:
            for s in (cfg.get("qcStandard") or {}).get("sections") or []:
                if str(s.get("n")) == str(n):
                    out["内容词"] += list(s.get("items") or [])

    # 每类去重（保持首次出现顺序）
    for _k in list(out.keys()):
        _seen = set()
        _uniq = []
        for _x in out[_k]:
            _s = str(_x)
            if _s not in _seen:
                _seen.add(_s)
                _uniq.append(_x)
        out[_k] = _uniq

    return out
'''

if "每类去重（保持首次出现顺序）" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点，把 return out 附近贴出来")
else:
    bak = TARGET.with_suffix(".py.bak_dedup")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已加关键词去重")