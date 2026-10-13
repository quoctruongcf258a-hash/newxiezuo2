# compare_pxx.py — 对比 PXX.md 标题 vs rings_items.json 名称
import json
import re
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
P = BASE / "prompts" / "01_规划"

# 读 rings_items.json
rings = json.loads((BASE / "rules" / "rings_items.json").read_text(encoding="utf-8"))
gh = rings.get("01_ 规划", {})
# 兼容不同 key
items = gh.get("环节") or gh.get("items") or []
by_code = {}
for it in items:
    if isinstance(it, dict):
        by_code[it.get("code")] = it.get("name")

# 读所有 PXX.md 的标题
print("=" * 90)
print(f"{'文件':12} {'# 任务：里的名字':30} {'rings_items 里的名字':30} {'是否匹配'}")
print("=" * 90)

for f in sorted(P.glob("P*.md")):
    code = f.stem  # P01 / P16 / P06-01 / P0Z-1
    # 匹配 rings 里的 name
    ring_name = by_code.get(code, "(未匹配)")
    
    # 读文件标题
    try:
        text = f.read_text(encoding="utf-8")
        m = re.search(r"#\s*任务[:：]\s*\S*\s*/\s*(.+)", text)
        file_name = m.group(1).strip() if m else "(没读到)"
    except Exception:
        file_name = "(读失败)"
    
    match = "✅" if file_name == ring_name else ("≈" if file_name.replace("规划", "") == ring_name.replace("规划", "") else "❌")
    print(f"{code:12} {file_name:30} {ring_name:30} {match}")