import json
from pathlib import Path

json_path = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== 01_规划 第一个环节的完整结构 ===")
if "01_规划" in data and "环节" in data["01_规划"] and data["01_规划"]["环节"]:
    print(json.dumps(data["01_规划"]["环节"][0], ensure_ascii=False, indent=2))

print("\n=== 所有环节的真实 id 与 name ===")
for phase in ["01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"]:
    print(f"\n--- {phase} ---")
    if phase in data and "环节" in data[phase]:
        for r in data[phase]["环节"]:
            # 尝试自动识别键名
            rid = r.get("id") or r.get("环ID") or r.get("编号") or r.get("key") or "无ID字段"
            name = r.get("name") or r.get("名称") or r.get("环节名") or "无名称字段"
            has_fields = "有fields" if "fields" in r else "无fields"
            print(f"  {rid} - {name} [{has_fields}]")
