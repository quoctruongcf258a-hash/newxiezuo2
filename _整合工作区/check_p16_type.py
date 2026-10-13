# check_p16_type.py — 查 P16 的 type / mode
import json
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

# 1) rings_items.json 里 P16
print("=" * 60)
print("1) rings_items.json → P16")
print("=" * 60)
rings = json.loads((BASE / "rules" / "rings_items.json").read_text(encoding="utf-8"))
for it in rings.get("01_ 规划", {}).get("环节", []):
    if it.get("code") in ("P16", "P17", "P09", "P01"):
        print(f"{it.get('code')}  {it.get('name')}")
        for k, v in it.items():
            if k not in ("name",):
                print(f"    {k} = {v!r}")
        print()

# 2) _load_phases 里 mode 映射
print("=" * 60)
print("2) _load_phases 里的 mode 映射")
print("=" * 60)
O = (BASE / "windows-use" / "_scratch" / "orchestrator.py").read_text(encoding="utf-8")
i = O.find("def _load_phases")
if i >= 0:
    print(O[i:i+1200])

# 3) run_program 里 fixed 分支
print("=" * 60)
print("3) run_program 里 fixed 分支")
print("=" * 60)
i = O.find('if ph.get("mode") == "fixed"')
if i >= 0:
    print(O[i:i+400])