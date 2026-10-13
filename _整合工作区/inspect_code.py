import json
from pathlib import Path

json_path = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

target_names = ["全书结构", "总纲规划", "粗纲规划", "简短细纲规划", "详细细纲规划"]

print("=== 5个新环的真实 code / name / fields ===")
for phase in ["01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"]:
    if phase in data and "环节" in data[phase]:
        for r in data[phase]["环节"]:
            name = r.get("name", "")
            if name in target_names:
                code = r.get("code", "无code")
                fields = r.get("fields", "未配置")
                print(f"\n--- {code} | {name} ---")
                print(f"  fields 类型: {type(fields)}")
                if isinstance(fields, list):
                    print(f"  fields 数量: {len(fields)}")
                    for f in fields:
                        print(f"    - {f}")
                elif isinstance(fields, dict):
                    print(f"  fields 键: {list(fields.keys())}")
                    for k, v in fields.items():
                        print(f"    {k}: {v}")
                else:
                    print(f"  fields 内容: {fields}")

print("\n=== 所有环节的 code 一览（用于确认编号方案）===")
for phase in ["01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"]:
    print(f"\n--- {phase} ---")
    if phase in data and "环节" in data[phase]:
        for r in data[phase]["环节"]:
            code = r.get("code", "无code")
            name = r.get("name", "无名")
            has_f = "★" if "fields" in r else " "
            print(f"  [{has_f}] {code} - {name}")
