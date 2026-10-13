import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_review_json")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# 改 _do_review_batch 的输出文件名为 .json
OLD = '    report_file = review_dir / "审核报告.md"'
NEW = '    report_file = review_dir / "全书结构.json"'

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 盲审输出改成 全书结构.json")
else:
    print("[WARN] 找不到锚点（可能已改）")
