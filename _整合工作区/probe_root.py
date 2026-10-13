# probe_root.py — 看 _project_root / 项目名怎么确定
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "_project_root / WORK 定义", "=" * 30)
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ["_project_root", "WORK =", "PROJECT_NAME",
                              "项目名", "OUTPUT_ROOT", "WORK_ROOT"]):
        print(f"{i:4d}| {ln[:140]}")

print()
print("=" * 30, "_project_root 函数全文", "=" * 30)
for i, ln in enumerate(lines):
    if ln.startswith("def _project_root"):
        for j in range(i, min(i+40, len(lines))):
            print(f"{j+1:4d}| {lines[j]}")
        break

print()
print("=" * 30, "所有含 WORK 的赋值（前 20 条）", "=" * 30)
n = 0
for i, ln in enumerate(lines, 1):
    if "WORK" in ln and "=" in ln and "==" not in ln:
        print(f"{i:4d}| {ln[:140]}")
        n += 1
        if n >= 20:
            break