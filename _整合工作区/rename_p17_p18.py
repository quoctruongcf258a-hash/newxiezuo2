import json, shutil
from pathlib import Path

p = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
bak = p.with_suffix(".json.bak_rename")
if not bak.exists():
    shutil.copy(p, bak)
    print(f"已备份：{bak.name}")

data = json.loads(p.read_text(encoding="utf-8"))
renames = {"详细细纲规划": "细纲", "前30章章纲": "前30章落地章纲"}
for ring in data["01_规划"]["环节"]:
    n = ring.get("name")
    if n in renames:
        ring["name"] = renames[n]
        print(f"  {ring.get('code')}: {n} → {renames[n]}")

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已写回：{p.name}")
