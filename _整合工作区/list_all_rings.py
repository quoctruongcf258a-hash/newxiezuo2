import json
from pathlib import Path

p = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
data = json.loads(p.read_text(encoding="utf-8"))

print("=" * 70)
print("全部环节（按阶段）")
print("=" * 70)
for phase_key in ["01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"]:
    if phase_key not in data:
        continue
    print(f"\n📁 {phase_key}")
    for ring in data[phase_key].get("环节", []):
        code = ring.get("code", "?")
        name = ring.get("name", "?")
        desc = (ring.get("desc") or "")[:60]
        print(f"  {code:10} {name:25} | {desc}")
