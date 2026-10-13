import re
from pathlib import Path

T2 = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text2 = T2.read_text(encoding="utf-8")

m = re.search(r"def _file_mode_task\(.*?(?=\n\ndef |\Z)", text2, re.DOTALL)
if m:
    print("=" * 70)
    print("_file_mode_task 完整代码")
    print("=" * 70)
    print(m.group(0))
else:
    print("❌ 找不到 _file_mode_task")
