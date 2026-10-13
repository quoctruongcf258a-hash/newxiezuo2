# fix_kw.py — 补丁1：keywords_for_phase 支持 fields；补丁2：截断 10 → 30
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")
changed = 0

# ── 补丁 1 ────────────────────────────────
OLD1 = '''    if program == "规划":
        # 内容词只取 desc 里 → 前面的部分（→ 后面是动作）
        _desc = (phase_cfg.get("desc") or "").strip()
        if _desc:
            _head = _desc
            for _sep in ("→", "->", "=>"):
                if _sep in _head:
                    _head = _head.split(_sep)[0]
                    break
            for _part in re.split(r"[+/、，,；;]+", _head):
                _p = _part.strip()
                if _p and len(_p) <= 12 and not _p.startswith("输出"):
                    out["内容词"].append(_p)
'''

NEW1 = '''    if program == "规划":
        # 优先用 fields（新环有明确字段列表）
        _fields = phase_cfg.get("fields") or []
        if _fields:
            out["内容词"] = [str(f) for f in _fields]
        else:
            # 回退：从 desc 拆（→ 后面是动作）
            _desc = (phase_cfg.get("desc") or "").strip()
            if _desc:
                _head = _desc
                for _sep in ("→", "->", "=>"):
                    if _sep in _head:
                        _head = _head.split(_sep)[0]
                        break
                for _part in re.split(r"[+/、，,；;]+", _head):
                    _p = _part.strip()
                    if _p and not _p.startswith("输出"):
                        out["内容词"].append(_p)
'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("✔ 补丁1：keywords_for_phase 支持 fields")
    changed += 1
else:
    print("✗ 补丁1 找不到锚点")
    i = text.find('if program == "规划":')
    if i >= 0:
        print("  附近：")
        print(text[i:i+500])

# ── 补丁 2a：内容词 ─────────────────────────
OLD2a = r'_kb += "\n  内容词：" + "、".join(_kw["内容词"][:10])'
NEW2a = r'_kb += "\n  内容词：" + "、".join(_kw["内容词"][:30])'

if OLD2a in text:
    text = text.replace(OLD2a, NEW2a, 1)
    print("✔ 补丁2a：内容词截断 10 → 30")
    changed += 1
else:
    print("✗ 补丁2a 找不到锚点")
    for kw in ['内容词']:
        j = text.find(f'_kw["{kw}"][:10]')
        if j >= 0:
            print(f"  附近（{kw}）：", repr(text[j-30:j+50]))

# ── 补丁 2b：动作词 ─────────────────────────
OLD2b = r'_kb += "\n  动作词：" + "、".join(_kw["动作词"][:10])'
NEW2b = r'_kb += "\n  动作词：" + "、".join(_kw["动作词"][:30])'

if OLD2b in text:
    text = text.replace(OLD2b, NEW2b, 1)
    print("✔ 补丁2b：动作词截断 10 → 30")
    changed += 1
else:
    print("✗ 补丁2b 找不到锚点")
    j = text.find('_kw["动作词"][:10]')
    if j >= 0:
        print("  附近（动作词）：", repr(text[j-30:j+50]))

if changed:
    bak = TARGET.with_suffix(".py.bak_kwfix")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 共 {changed}/3 处已改")
else:
    print("\n没有改动")