# probe_mixsend.py — 找 mix_send.send + orchestrator 381-420
from pathlib import Path

# 1) 全盘找 mix_send.py
print("=" * 30, "找 mix_send.py", "=" * 30)
for root in [Path(r"F:\赛马23环整合工作室"), Path(r"F:\Program")]:
    if not root.exists():
        continue
    for p in root.rglob("mix_send.py"):
        print(f"  {p}  ({p.stat().st_size} 字节)")

# 2) orchestrator.py 381-420 行
print()
print("=" * 30, "orchestrator.py 375-425 行", "=" * 30)
O = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = O.read_text(encoding="utf-8").splitlines()
for i in range(374, 425):
    if i < len(lines):
        print(f"{i+1:4d}| {lines[i]}")