# fix_kw_plan.py
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

if not TARGET.exists():
    print("找不到 orchestrator.py")
    raise SystemExit(1)

lines = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

i_func = None
for i, ln in enumerate(lines):
    if ln.startswith("def keywords_for_phase"):
        i_func = i
        break
if i_func is None:
    print("找不到 def keywords_for_phase")
    raise SystemExit(1)

i_plan = None
for i in range(i_func, len(lines)):
    if lines[i].strip() == 'if program == "规划":':
        i_plan = i
        break

i_write = None
for i in range((i_plan or 0) + 1, len(lines)):
    if lines[i].strip() == 'if program == "写作":':
        i_write = i
        break

if i_plan is None or i_write is None:
    print(f"定位失败 i_plan={i_plan} i_write={i_write}")
    raise SystemExit(1)

print(f"定位：规划段第 {i_plan+1} 行，写作段第 {i_write+1} 行")

bak = TARGET.with_suffix(".py.bak_kwplan")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

NEW_PLAN = '''    if program == "规划":
        _desc = (phase_cfg.get("desc") or "").strip()
        if _desc:
            for _part in re.split(r"[+\u2192/\u3001\uff0c,\uff1b;]+", _desc):
                _p = _part.strip()
                if _p and len(_p) <= 12 and not _p.startswith("输出"):
                    out["内容词"].append(_p)

'''

new_lines = lines[:i_plan] + [NEW_PLAN] + lines[i_write:]
text = "".join(new_lines)

if "\nimport re\n" not in text:
    text = text.replace("import argparse\n", "import argparse\nimport re\n", 1)
    print("已补 import re")

TARGET.write_text(text, encoding="utf-8")
print("✔ 已写回")