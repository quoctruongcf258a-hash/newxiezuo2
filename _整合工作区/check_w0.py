import json
from pathlib import Path

rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))

print("=== 02_写作 阶段所有环的 code / name / key ===")
for ring in rings["02_写作"]["环节"]:
    print(f"  code={ring.get('code'):<8} name={ring.get('name'):<20} key={ring.get('key')}")
