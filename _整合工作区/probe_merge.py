# probe_merge.py — 看 do_merge + build_merge_task + PROMPT_MERGE
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

def show_func(name, maxn=60):
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

show_func("do_merge", 80)

print()
print("=" * 30, "tasks.py 里 build_merge_task", "=" * 30)
T = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
tlines = T.read_text(encoding="utf-8").splitlines()
start = None
for i, ln in enumerate(tlines):
    if "def build_merge_task" in ln:
        start = i
        break
if start is not None:
    end = start + 1
    while end < len(tlines):
        ln = tlines[end]
        if ln.startswith("def ") and end > start + 3:
            break
        end += 1
        if end - start > 60:
            break
    for i in range(start, end):
        print(f"{i+1:4d}| {tlines[i]}")
else:
    print("没找到 build_merge_task")

print()
print("=" * 30, "orchestrator.py 里 PROMPT_MERGE 相关", "=" * 30)
for i, ln in enumerate(lines, 1):
    if "MERGE" in ln or "拼接" in ln and ("prompt" in ln.lower() or "tpl" in ln):
        print(f"{i:4d}| {ln[:130]}")