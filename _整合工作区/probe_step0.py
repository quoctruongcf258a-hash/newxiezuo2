# probe_step0.py — 看 步骤0 / 00_初始化 的结构
from pathlib import Path
import json

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

# 1) prompts 下和「步骤0」「初始化」相关的目录
print("=" * 70)
print("1) prompts/ 下候选目录")
print("=" * 70)
for name in ["步骤0", "00_初始化"]:
    d = BASE / "prompts" / name
    print(f"\n📁 prompts/{name}/")
    if d.exists():
        for f in sorted(d.iterdir()):
            if f.is_file():
                print(f"    {f.name}  ({f.stat().st_size} 字节)")
    else:
        print("    (不存在)")

# 2) AI指派协作 下的步骤0
print()
print("=" * 70)
print("2) AI指派协作/prompts/步骤0/")
print("=" * 70)
d2 = BASE / "AI指派协作" / "prompts" / "步骤0"
if d2.exists():
    for f in sorted(d2.iterdir()):
        if f.is_file():
            print(f"    {f.name}  ({f.stat().st_size} 字节)")
else:
    print("    (不存在)")

# 3) 00_初始化 的产物目录
print()
print("=" * 70)
print("3) output/女王归来_test/00_初始化/")
print("=" * 70)
d3 = BASE / "output" / "女王归来_test" / "00_初始化"
if d3.exists():
    for f in sorted(d3.iterdir()):
        if f.is_file():
            print(f"    {f.name}  ({f.stat().st_size} 字节)")

# 4) rings_items.json 里有没有 00_初始化 / 步骤0
print()
print("=" * 70)
print("4) rings_items.json 顶层 keys")
print("=" * 70)
data = json.loads((BASE / "rules" / "rings_items.json").read_text(encoding="utf-8"))
for k in data.keys():
    v = data[k]
    if isinstance(v, dict):
        n = len(v.get("环节", []))
        print(f"  {k!r}  →  {n} 环")
    else:
        print(f"  {k!r}  →  {type(v).__name__}")

# 5) orchestrator 里含「步骤0」「初始化」的行
print()
print("=" * 70)
print("5) orchestrator.py 里含 步骤0/初始化 的行")
print("=" * 70)
O = BASE / "windows-use" / "_scratch" / "orchestrator.py"
text = O.read_text(encoding="utf-8")
for i, ln in enumerate(text.splitlines(), 1):
    if "步骤0" in ln or ("初始化" in ln and "00" in ln):
        print(f"{i:4d}| {ln[:140]}")