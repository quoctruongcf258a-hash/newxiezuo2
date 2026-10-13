# probe_more.py — 查 PROMPTS 常量 + 01_规划 提示词 + P01 配置
from pathlib import Path
import json

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

# 1) PROMPTS 常量指向哪里
print("=" * 70)
print("1) PROMPTS 常量")
print("=" * 70)
O = BASE / "windows-use" / "_scratch" / "orchestrator.py"
text = O.read_text(encoding="utf-8")
for i, ln in enumerate(text.splitlines(), 1):
    if "PROMPTS" in ln and "=" in ln and "load_prompt" not in ln:
        print(f"{i:4d}| {ln[:130]}")

# 2) 01_规划 提示词文件（3 个候选目录）
print()
print("=" * 70)
print("2) 01_规划 提示词文件（各目录）")
print("=" * 70)
for dir_ in [
    BASE / "prompts" / "01_规划",
    BASE / "output" / "女王归来" / "config" / "prompts" / "01_规划",
    BASE / "AI指派协作" / "prompts" / "01_规划",
]:
    print(f"\n📁 {dir_}")
    if dir_.exists():
        for p in sorted(dir_.iterdir()):
            if p.is_file():
                print(f"    {p.name}  ({p.stat().st_size} 字节)")
    else:
        print("    (不存在)")

# 3) P01 的真实配置
print()
print("=" * 70)
print("3) rings_items.json → 01_规划 全部环节")
print("=" * 70)
d = json.loads((BASE / "rules" / "rings_items.json").read_text(encoding="utf-8"))
gh = d.get("01_ 规划", {})
print(f"01_规划 keys: {list(gh.keys())}")
print(f"环数: {gh.get('环数')}")
items = gh.get("环节", [])
print(f"环节数: {len(items)}")
for it in items[:3]:
    print(f"\n  第一个：{it.get('code')}  {it.get('name')}")
    print(f"    desc = {it.get('desc', '(空)')[:120]}")
    print(f"    type = {it.get('type')}")