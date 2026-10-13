from pathlib import Path
import re

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = target.read_text(encoding="utf-8")

# 找 _resolve_ai_name 的完整实现
m = re.search(r"def _resolve_ai_name\(.*?(?=\n\ndef |\n\n# |\Z)", text, re.DOTALL)
if m:
    print("=" * 70)
    print("=== _resolve_ai_name 当前代码 ===")
    print("=" * 70)
    print(m.group(0))
else:
    print("❌ 找不到 _resolve_ai_name")

# 顺便看 today.json 的 workbuddy label
import json
print()
print("=" * 70)
print("=== today.json 里的 opened ===")
print("=" * 70)
tj = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\today.json")
data = json.loads(tj.read_text(encoding="utf-8"))
for item in data.get("opened") or []:
    print(f"  key={item.get('key')!r:15} label={item.get('label')!r}")
