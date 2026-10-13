# check_fields.py — 看 rings_items.json 里 5 个新环有没有带 fields
import json
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
data = json.loads(P.read_text(encoding="utf-8"))

print("顶层类型:", type(data).__name__)
if isinstance(data, dict):
    print("顶层 keys:", list(data.keys()))

targets = {"P09", "P14", "P15", "P16", "P17"}
found = []

def walk(obj, path=""):
    if isinstance(obj, dict):
        code = obj.get("code") or obj.get("id") or ""
        if code in targets:
            found.append((path, obj))
        for k, v in obj.items():
            walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            walk(x, f"{path}[{i}]")

walk(data)

print(f"\n找到 {len(found)} 条目标环")
for path, it in found:
    print(f"\n--- {path} ---")
    print("keys:", list(it.keys()))
    print("code:", it.get("code") or it.get("id"))
    print("name:", it.get("name"))
    print("fields:", it.get("fields"))