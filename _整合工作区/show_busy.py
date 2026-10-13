# show_busy.py — 打印 is_ai_busy + wait_idle 的实际代码
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
lines = P.read_text(encoding="utf-8").splitlines()

# 找 is_ai_busy 和 wait_idle
for name in ["is_ai_busy", "wait_idle", "check_running"]:
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith(f"def {name}"):
            start = i
            break
    if start is None:
        print(f"=== {name}: 未找到 ===")
        print()
        continue
    print(f"=== {name} (第 {start+1} 行) ===")
    end = start + 1
    while end < len(lines) and not (lines[end].startswith("def ") or lines[end].startswith("# ═")):
        end += 1
    for i in range(start, min(end, start + 60)):
        print(f"{i+1:4d}| {lines[i]}")
    print()