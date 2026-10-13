from pathlib import Path
TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = TARGET.read_text(encoding="utf-8", errors="ignore").splitlines()
print("=== 3500-3520 行 ===")
for i in range(3499, min(3520, len(lines))):
    print(f"{i+1:4d}| {lines[i]}")
