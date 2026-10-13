# final_check.py — 确认 P16 type + 看 P16 dry-run 块数
import json
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

# 1) rings_items.json 的 type
print("=" * 60)
print("1) P16 / P17 / P01 的 type")
print("=" * 60)
d = json.loads((BASE / "rules" / "rings_items.json").read_text(encoding="utf-8"))
for it in d.get("01_ 规划", {}).get("环节", []):
    if it.get("code") in ("P01", "P09", "P16", "P17"):
        print(f"  {it.get('code')}  {it.get('name')}  type={it.get('type')!r}  "
              f"segment_mode={it.get('segment_mode')!r}  fields={bool(it.get('fields'))}")
print()
print("  05_出厂 的 type：")
for it in d.get("05_出厂", {}).get("环节", []):
    print(f"    {it.get('code')}  {it.get('name')}  type={it.get('type')!r}")

# 2) P16 dry-run 输出
print()
print("=" * 60)
print("2) P16 dry-run 日志关键行")
print("=" * 60)
p = BASE / "windows-use" / "_scratch" / "_check_p16b.txt"
if p.exists():
    t = p.read_bytes().decode("gb18030", errors="ignore")
    for ln in t.splitlines():
        if any(k in ln for k in ["共", "块", "参战", "卷", "固定流程", "环节", "错误"]):
            print(f"  {ln[:140]}")
else:
    print("  日志不存在")