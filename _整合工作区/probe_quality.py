# probe_quality.py — 探查 4 个质量问题现状
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

def show(name, maxn=45):
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
        if end - start > maxn:
            break
    for i in range(start, end):
        print(f"{i+1:4d}| {lines[i]}")

# 1) keywords_for_phase
show("keywords_for_phase", 60)

# 2) plan_direction_standard
show("plan_direction_standard", 40)

# 3) _upstream_files
show("_upstream_files", 55)