# show_load_phases.py — 看 _load_phases 完整定义
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

start = None
for i, ln in enumerate(lines):
    if ln.startswith("def _load_phases"):
        start = i
        break

print(f"--- _load_phases 从第 {start+1} 行起 ---")
end = start + 1
while end < len(lines):
    ln = lines[end]
    if ln.startswith("def ") and end > start + 3:
        break
    end += 1
    if end - start > 100:
        break

for i in range(start, end):
    print(f"{i+1:4d}| {lines[i]}")