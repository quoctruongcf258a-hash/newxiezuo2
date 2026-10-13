# show_write_note.py — 看 format_note 写作分支（289 行附近）
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "第 280-320 行", "=" * 30)
for i in range(279, 320):
    if i < len(lines):
        print(f"{i+1:4d}| {lines[i]}")