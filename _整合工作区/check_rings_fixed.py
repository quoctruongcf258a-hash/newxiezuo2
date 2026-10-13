import json
from pathlib import Path

json_path = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

phases = ['01_规划', '02_写作', '03_去AI', '04_审核', '05_出厂']
total_rings = 0
target_rings = ["P09", "P14", "P15", "P16", "P17"]
found_targets = set()

print("=== 环节统计 ===")
for phase in phases:
    if phase in data and "环节" in data[phase]:
        rings_list = data[phase]["环节"]
        count = len(rings_list)
        total_rings += count
        print(f"  {phase}: {count} 环")

print(f"\n总环节数: {total_rings} (预期: 51)")

print("\n=== 目标新环 fields 检查 ===")
for phase in phases:
    if phase in data and "环节" in data[phase]:
        for ring in data[phase]["环节"]:
            ring_id = ring.get("id", "")
            if ring_id in target_rings:
                found_targets.add(ring_id)
                fields = ring.get("fields", "未配置")
                name = ring.get("name", "无名")
                print(f"  {ring_id} ({name}): {fields}")

missing = set(target_rings) - found_targets
if missing:
    print(f"\n⚠️ 未找到的环: {missing}")
else:
    print("\n✅ 5个目标新环全部找到")
