# check_p16_type2.py — 查 P16 的 type（两处源头）
import json
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

# 1) rings_items.json
print("=" * 60)
print("1) rings_items.json 里所有 type=fixed 的环节")
print("=" * 60)
rings = json.loads((BASE / "rules" / "rings_items.json").read_text(encoding="utf-8"))
for stage in rings:
    if not stage.endswith("规划") and not stage.endswith("写作") and not stage.endswith("去AI") and not stage.endswith("审核") and not stage.endswith("出厂"):
        continue
    for it in rings[stage].get("环节", []):
        if it.get("type") == "fixed":
            print(f"  [{stage}] {it.get('code')}  {it.get('name')}  type={it.get('type')}")

# 2) 环节模板.json
print()
print("=" * 60)
print("2) 环节模板.json 里 P16 的 type")
print("=" * 60)
tmpl = BASE / "rules" / "环节模板.json"
if tmpl.exists():
    data = json.loads(tmpl.read_text(encoding="utf-8"))
    for r in data.get("固定环", []):
        if r.get("code") in ("P16", "P17", "P09"):
            print(f"  {r.get('code')}  {r.get('name')}")
            print(f"     type = {r.get('type')!r}")
            print(f"     segment_mode = {r.get('segment_mode')!r}")
            print(f"     fields = {bool(r.get('fields'))}")
            print()
else:
    print("  环节模板.json 不存在")

# 3) project_expander.py 里 type 怎么定
print("=" * 60)
print("3) project_expander.py 里 type 赋值")
print("=" * 60)
pe = BASE / "app" / "project_expander.py"
if pe.exists():
    t = pe.read_text(encoding="utf-8")
    for i, ln in enumerate(t.splitlines(), 1):
        if "type" in ln.lower() and ("fixed" in ln or "mesh" in ln or "type" in ln):
            print(f"{i:4d}| {ln[:130]}")