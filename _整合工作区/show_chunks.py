# show_chunks.py — 看 chunks_for_phase 和 do_produce 的切块逻辑
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

# 找 chunks_for_phase
def show_func(name, max_lines=60):
    print("=" * 30, name, "=" * 30)
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith(f"def {name}"):
            start = i
            break
    if start is None:
        print("没找到")
        return
    end = start + 1
    while end < len(lines):
        ln = lines[end]
        if ln.startswith("def ") and end > start + 3:
            break
        end += 1
        if end - start > max_lines:
            break
    for i in range(start, end):
        print(f"{i+1:4d}| {lines[i]}")

show_func("chunks_for_phase")
print()
show_func("run_mesh_phase", 80)