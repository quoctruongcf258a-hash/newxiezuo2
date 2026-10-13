from pathlib import Path
import re

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

m = re.search(r"def _run_batch_mesh\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    print("=" * 70)
    print("=== _run_batch_mesh 真实代码（前 30 行）===")
    print("=" * 70)
    for i, ln in enumerate(m.group(0).splitlines()[:30], 1):
        print(f"{i:4d}| {ln}")
