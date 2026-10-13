from pathlib import Path
import re

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = target.read_text(encoding="utf-8")

m = re.search(r"def _judge_task_status\(.*?(?=\n\ndef |\n\n# |\Z)", text, re.DOTALL)
if m:
    print("=" * 70)
    print("=== _judge_task_status 当前代码 ===")
    print("=" * 70)
    print(m.group(0))
else:
    print("❌ 找不到 _judge_task_status")
