# fix_load_phases.py — 让 _load_phases 保留 fields / segment_mode 等原字段
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''                for item in items:
                    out.append({
                        "key": item.get("name") or item.get("code"),
                        "code": item.get("code"),
                        "mode": item.get("type") or "mesh",
                        "stage": program,
                        "supp": False,
                        "desc": item.get("desc", ""),
                    })
'''

NEW = '''                for item in items:
                    d = dict(item)  # 先保留原字段（fields / segment_mode / segment_size 等）
                    d.update({
                        "key": item.get("name") or item.get("code"),
                        "code": item.get("code"),
                        "mode": item.get("type") or "mesh",
                        "stage": program,
                        "supp": False,
                        "desc": item.get("desc", ""),
                    })
                    out.append(d)
'''

text = TARGET.read_text(encoding="utf-8")

if "先保留原字段" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点，把这段代码贴出来")
else:
    bak = TARGET.with_suffix(".py.bak_loadphases")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已改：_load_phases 保留 fields / segment_mode 等原字段")