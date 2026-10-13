# probe_runprogram.py — 看 run_program 完整定义 + main 尾部
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

def show(start, end, title):
    print("=" * 30, title, "=" * 30)
    for i in range(start-1, min(end, len(lines))):
        print(f"{i+1:4d}| {lines[i]}")

show(1305, 1380, "run_program 定义")
show(1480, 1537, "main 尾部")