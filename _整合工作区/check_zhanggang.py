import json
from pathlib import Path

rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))

print("=== 全文搜索所有含「章纲」的环节 ===")
for phase_key in ["01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"]:
    if phase_key not in rings:
        continue
    found = False
    for ring in rings[phase_key].get("环节", []):
        text = (ring.get("name", "") + " " + ring.get("desc", "") + " " + str(ring.get("fields") or ""))
        if "章纲" in text:
            if not found:
                print(f"\n📁 {phase_key}")
                found = True
            print(f"  ★ {ring.get('code')} {ring.get('name')}")
            print(f"    desc: {ring.get('desc', '')[:150]}")

print("\n\n=== 02_写作 完整环节列表 ===")
for ring in rings.get("02_写作", {}).get("环节", []):
    print(f"  {ring.get('code')}  {ring.get('name')}")
    print(f"    desc: {ring.get('desc', '')[:120]}")
    if ring.get("fields"):
        print(f"    fields: {ring['fields']}")
    print()
