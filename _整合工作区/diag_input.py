from pathlib import Path

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()

# ── 1. _upstream_files 完整代码 ──
print("=== _upstream_files 完整代码 ===")
i_func = None
for i, ln in enumerate(lines):
    if ln.startswith("def _upstream_files"):
        i_func = i
        break
if i_func is not None:
    end = i_func + 1
    while end < len(lines) and end < i_func + 150:
        if end > i_func + 1 and lines[end].startswith("def "):
            break
        end += 1
    for j in range(i_func, end):
        print(f"{j+1:4d}| {lines[j]}")

# ── 2. phase_input 完整代码 ──
print("\n\n=== phase_input 完整代码 ===")
i_pi = None
for i, ln in enumerate(lines):
    if ln.startswith("def phase_input"):
        i_pi = i
        break
if i_pi is not None:
    end = i_pi + 1
    while end < len(lines) and end < i_pi + 120:
        if end > i_pi + 1 and lines[end].startswith("def "):
            break
        end += 1
    for j in range(i_pi, end):
        print(f"{j+1:4d}| {lines[j]}")
