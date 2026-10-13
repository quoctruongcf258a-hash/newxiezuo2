from pathlib import Path
import re

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

m = re.search(r"def _maybe_extract_split\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    print("=" * 70)
    print("=== _maybe_extract_split 当前代码 ===")
    print("=" * 70)
    print(m.group(0))
else:
    print("❌ 找不到")
