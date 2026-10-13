# probe_kw_block.py — 看 keywords_for_phase 调用处（1150-1195 行）
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "第 1145-1200 行", "=" * 30)
for i in range(1144, 1200):
    if i < len(lines):
        print(f"{i+1:4d}| {lines[i]}")