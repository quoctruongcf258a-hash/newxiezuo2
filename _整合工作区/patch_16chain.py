import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
NEWFILE = Path(r"F:\赛马23环整合工作室\_整合工作区\new_build_task.txt")

text = TARGET.read_text(encoding="utf-8")
new_body = NEWFILE.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_16chain")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print("已备份：", bak.name)

anchor = "def _do_review_batch("
p = text.find(anchor)
if p < 0:
    print("[FAIL] 没找到 _do_review_batch")
    raise SystemExit(1)

marker = '    def build_task(ai_key):\n        return f"""【任务：盲审】'
i = text.find(marker, p)
if i < 0:
    print("[FAIL] 没找到 build_task 起点")
    raise SystemExit(1)

end_marker = '\n"""\n'
j = text.find(end_marker, i)
if j < 0:
    print("[FAIL] 没找到 build_task 结束")
    raise SystemExit(1)

end = j + len(end_marker)
text = text[:i] + new_body + text[end:]
TARGET.write_text(text, encoding="utf-8")
print("[OK] 已替换 _do_review_batch 里的 build_task")
