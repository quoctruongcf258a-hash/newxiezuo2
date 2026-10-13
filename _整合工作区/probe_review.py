# probe_review.py — 看 do_review 完整代码 + build_review_task
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

start = None
for i, ln in enumerate(lines):
    if ln.startswith("def do_review"):
        start = i
        break

print(f"--- do_review 从第 {start+1} 行起 ---")
end = start + 1
while end < len(lines):
    ln = lines[end]
    if ln.startswith("def ") and end > start + 3:
        break
    end += 1
    if end - start > 90:
        break

for i in range(start, end):
    print(f"{i+1:4d}| {lines[i]}")

print()
print("=" * 30, "build_review_task（tasks.py）", "=" * 30)
T = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
tl = T.read_text(encoding="utf-8").splitlines()
s2 = None
for i, ln in enumerate(tl):
    if "def build_review_task" in ln:
        s2 = i
        break
if s2 is not None:
    e2 = s2 + 1
    while e2 < len(tl):
        if tl[e2].startswith("def ") and e2 > s2 + 3:
            break
        e2 += 1
        if e2 - s2 > 70:
            break
    for i in range(s2, e2):
        print(f"{i+1:4d}| {tl[i]}")