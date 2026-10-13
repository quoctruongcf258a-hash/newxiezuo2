# find_sources.py — 找章节数 / 卷数 / cfg 来源
import json
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

print("=" * 30, "1) rings_items.json 顶层", "=" * 30)
rings = json.loads((BASE / "rules" / "rings_items.json").read_text(encoding="utf-8"))
for k, v in rings.items():
    if isinstance(v, dict):
        print(f"  {k} → keys={list(v.keys())[:8]}")
    else:
        print(f"  {k} = {v!r}")

print()
print("=" * 30, "2) 01_规划 顶层字段", "=" * 30)
gh = rings.get("01_ 规划", {})
for k, v in gh.items():
    if k == "环节":
        print(f"  环节: {len(v)} 条")
    else:
        print(f"  {k} = {v!r}")

print()
print("=" * 30, "3) 项目信息.json", "=" * 30)
pinfo = BASE / "output" / "女王归来" / "00_初始化" / "项目信息.json"
if pinfo.exists():
    d = json.loads(pinfo.read_text(encoding="utf-8"))
    for k, v in d.items():
        s = str(v)
        print(f"  {k} = {s[:80]}")
else:
    print("  不存在:", pinfo)

print()
print("=" * 30, "4) apps.json 里跟卷/章相关的字段", "=" * 30)
apps = json.loads((BASE / "app" / "apps.json").read_text(encoding="utf-8"))
def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if any(t in str(k) for t in ["卷", "章", "volume", "chapter", "segment"]):
                print(f"  {path}.{k} = {str(v)[:120]}")
            walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            walk(x, f"{path}[{i}]")
walk(apps)