import json
from pathlib import Path

# 你的 rings_items.json 绝对路径
json_path = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 兼容数据结构，防止报错
if isinstance(data, dict):
    rings = data.get("rings", [])
    if not rings and "01_规划" in data:
        # 如果存在 phase 键结构，自动拍平
        rings = []
        for k, v in data.items():
            if isinstance(v, list):
                rings.extend(v)
elif isinstance(data, list):
    rings = data
else:
    rings = []

print(f"总环节数: {len(rings)}")

from collections import Counter
phase_counts = Counter()
program_counts = Counter()

for ring in rings:
    phase = ring.get("phase", "未知")
    program = ring.get("program", "未知")
    phase_counts[phase] += 1
    program_counts[program] += 1

print("\n按 phase 统计:")
for k, v in phase_counts.items():
    print(f"  {k}: {v}")

print("\n按 program 统计:")
for k, v in program_counts.items():
    print(f"  {k}: {v}")

# 检查目标新环的 fields
target_rings = ["P09", "P14", "P15", "P16", "P17"]
print("\n目标新环的 fields 检查:")
for ring in rings:
    ring_id = ring.get("id", "")
    if ring_id in target_rings:
        fields = ring.get("fields", "未配置")
        name = ring.get("name", "无名")
        print(f"  {ring_id} ({name}): {fields}")
