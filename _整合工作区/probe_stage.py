# probe_stage.py — 看 STAGE_MAP + 05_出厂 在系统里怎么跑的
import json
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "STAGE_MAP 定义（130-145 行）", "=" * 30)
for i in range(129, 150):
    if i < len(lines):
        print(f"{i+1:4d}| {lines[i]}")

print()
print("=" * 30, "05_出厂 在 orchestrator 里的引用", "=" * 30)
for i, ln in enumerate(lines, 1):
    if "出厂" in ln:
        print(f"{i:4d}| {ln[:130]}")

print()
print("=" * 30, "rings_items.json 里 05_出厂 的环节", "=" * 30)
BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
rings = json.loads((BASE / "rules" / "rings_items.json").read_text(encoding="utf-8"))
ch = rings.get("05_出厂", {})
print("keys:", list(ch.keys()))
for it in ch.get("环节", []):
    print(f"  {it.get('code')}  {it.get('name')}  type={it.get('type')}")

print()
print("=" * 30, "phases.json 里 05_出厂", "=" * 30)
ph = json.loads((BASE / "rules" / "phases.json").read_text(encoding="utf-8"))
for k in ph.keys():
    if "出厂" in k or "审核" in k:
        print(f"{k}: {ph[k]}")