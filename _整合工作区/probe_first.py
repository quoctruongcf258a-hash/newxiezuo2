# probe_first.py — 探查第一个环节的配置和提示词
import json
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

# 1) rings_items.json 里的 01_规划 环节
print("=" * 70)
print("1) rings_items.json → 01_规划 环节清单")
print("=" * 70)
rings = json.loads((BASE / "rules" / "rings_items.json").read_text(encoding="utf-8"))
for it in rings.get("01_ 规划", {}).get("环节", [])[:5]:
    print(f"  {it.get('code')}  {it.get('name')}")
    print(f"     desc: {it.get('desc', '')[:100]}")
    print(f"     type: {it.get('type')}  mode: {it.get('mode')}")
    if it.get('fields'):
        print(f"     fields: {it.get('fields')}")
    print()

# 2) phases.json 里的 01_规划 环节
print("=" * 70)
print("2) phases.json → 01_规划")
print("=" * 70)
ph = json.loads((BASE / "rules" / "phases.json").read_text(encoding="utf-8"))
print(f"顶层 keys: {list(ph.keys())}")
huan = ph.get("环节", {})
print(f"环节 keys: {list(huan.keys())}")
gh = huan.get("01_规划", [])
for x in gh[:5]:
    if isinstance(x, dict):
        print(f"  {x.get('name')}")
    else:
        print(f"  {x}")
print()

# 3) prompts/01_规划/ 目录
print("=" * 70)
print("3) config/prompts/01_规划/ 提示词文件")
print("=" * 70)
prompts = BASE / "config" / "prompts" / "01_规划"
if prompts.exists():
    for p in sorted(prompts.iterdir()):
        if p.is_file():
            print(f"  {p.name}  ({p.stat().st_size} 字节)")
else:
    print("  目录不存在")

print()
print("=" * 70)
print("4) orchestrator.py 里 compose_prompt 逻辑")
print("=" * 70)
o = (BASE / "windows-use" / "_scratch" / "orchestrator.py").read_text(encoding="utf-8")
i = o.find("def compose_prompt")
if i >= 0:
    print(o[i:i+1200])