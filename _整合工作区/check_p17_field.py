import json
from pathlib import Path

rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))

for ring in rings["01_规划"]["环节"]:
    if ring.get("name") == "详细细纲规划":
        for i, f in enumerate(ring.get("fields") or []):
            # 显示每个字段的 repr，能看出隐藏空格
            if "归" in f:
                print(f"  [{i}] {repr(f)}")
        break
