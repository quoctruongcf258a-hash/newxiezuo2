# probe_prompts.py — 摸清 prompts 结构
from pathlib import Path
import json

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

print("=" * 70)
print("1) 所有 prompts 目录位置")
print("=" * 70)
for p in BASE.rglob("prompts"):
    if p.is_dir():
        print(f"\n📁 {p}")
        for x in sorted(p.iterdir()):
            mark = "📁" if x.is_dir() else "  "
            print(f"  {mark} {x.name}")

print()
print("=" * 70)
print("2) load_prompt 怎么找文件")
print("=" * 70)
O = BASE / "windows-use" / "_scratch" / "orchestrator.py"
text = O.read_text(encoding="utf-8")
i = text.find("def load_prompt")
if i >= 0:
    j = text.find("\ndef ", i+10)
    print(text[i:j])

print()
print("=" * 70)
print("3) 00_初始化 当前 3 个文件")
print("=" * 70)
init = BASE / "output" / "女王归来_test" / "00_初始化"
if init.exists():
    for p in sorted(init.iterdir()):
        if p.is_file():
            print(f"  {p.name}  ({p.stat().st_size} 字节)")

print()
print("=" * 70)
print("4) P01 的 desc / fields")
print("=" * 70)
d = json.loads((BASE / "rules" / "rings_items.json").read_text(encoding="utf-8"))
for it in d.get("01_ 规划", {}).get("环节", [])[:3]:
    print(f"  {it.get('code')}  {it.get('name')}")
    print(f"    desc: {it.get('desc', '')[:150]}")
    print(f"    fields: {it.get('fields')}")
    print()