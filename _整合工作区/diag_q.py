import json
from pathlib import Path

rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))
print("=== 04_审核 各环节完整配置 ===")
for ring in rings["04_审核"]["环节"]:
    print(f"\n--- {ring.get('code')} {ring.get('name')} ---")
    print(json.dumps(ring, ensure_ascii=False, indent=2)[:400])

# Q1~Q9 哪些需要按章拆？看 type
print("\n\n=== 分类 ===")
for ring in rings["04_审核"]["环节"]:
    code = ring.get("code")
    name = ring.get("name")
    typ = ring.get("type")
    mode = ring.get("mode")
    print(f"  {code} {name}  type={typ} mode={mode}")
