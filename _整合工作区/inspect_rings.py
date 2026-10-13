import json
from pathlib import Path

json_path = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== 顶层类型 ===")
print(type(data))
print("=== 顶层 keys ===")
print(list(data.keys()))

if isinstance(data, dict):
    for k, v in data.items():
        print(f"\n--- 键: {k} ---")
        print(f"  类型: {type(v)}")
        if isinstance(v, dict):
            print(f"  子键: {list(v.keys())[:10]}")
        elif isinstance(v, list):
            print(f"  列表长度: {len(v)}")
            if len(v) > 0:
                print(f"  第一个元素类型: {type(v[0])}")
                if isinstance(v[0], dict):
                    print(f"  第一个元素的键: {list(v[0].keys())}")
