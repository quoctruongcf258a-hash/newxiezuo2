# fix_fixed_type.py — 修 P01~P27 的 type（都是 mesh）
import shutil
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

# ─── 修 1：project_expander.py ───
PE = BASE / "app" / "project_expander.py"
text = PE.read_text(encoding="utf-8")

OLD1 = '        item = {**r, "type": "fixed"}'
NEW1 = '''        # 固定环默认 mesh（走网格赛马）；只有出厂类的才标 fixed
        item = {**r}
        if not item.get("type"):
            item["type"] = "mesh"
        # 出厂类（05_出厂）保持 fixed
        if item.get("code", "").startswith("05-"):
            item["type"] = "fixed"'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    bak = PE.with_suffix(".py.bak_fixed")
    if not bak.exists():
        shutil.copy(PE, bak)
        print(f"已备份：{bak.name}")
    PE.write_text(text, encoding="utf-8")
    print("✔ project_expander.py 已修")
else:
    print("✗ project_expander 锚点不匹配")
    i = text.find('"type": "fixed"')
    if i >= 0:
        print(repr(text[i-100:i+100]))

# ─── 修 2：_load_phases 加兜底 ───
O = BASE / "windows-use" / "_scratch" / "orchestrator.py"
text2 = O.read_text(encoding="utf-8")

OLD2 = '''                for item in items:
                    d = dict(item)  # 先保留原字段（fields / segment_mode / segment_size 等）
                    d.update({
                        "key": item.get("name") or item.get("code"),
                        "code": item.get("code"),
                        "mode": item.get("type") or "mesh",
                        "stage": program,
                        "supp": False,
                        "desc": item.get("desc", ""),
                    })
                    out.append(d)'''

NEW2 = '''                for item in items:
                    d = dict(item)  # 先保留原字段（fields / segment_mode / segment_size 等）
                    # 兜底：有 fields 或 segment_mode 的环节一律走 mesh（不是 fixed）
                    _m = item.get("type") or "mesh"
                    if _m == "fixed" and (item.get("fields") or item.get("segment_mode")):
                        _m = "mesh"
                    d.update({
                        "key": item.get("name") or item.get("code"),
                        "code": item.get("code"),
                        "mode": _m,
                        "stage": program,
                        "supp": False,
                        "desc": item.get("desc", ""),
                    })
                    out.append(d)'''

if "有 fields 或 segment_mode 的环节一律走 mesh" in text2:
    print("✔ _load_phases 已改过")
elif OLD2 in text2:
    bak2 = O.with_suffix(".py.bak_fixed")
    if not bak2.exists():
        shutil.copy(O, bak2)
        print(f"已备份：{bak2.name}")
    text2 = text2.replace(OLD2, NEW2, 1)
    O.write_text(text2, encoding="utf-8")
    print("✔ _load_phases 已加兜底")
else:
    print("✗ _load_phases 锚点不匹配")