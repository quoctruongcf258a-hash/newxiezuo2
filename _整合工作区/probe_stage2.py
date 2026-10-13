# probe_stage2.py — 看 _STAGE_DIR_MAP / PROGRAM_GATES / mode 处理
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "_STAGE_DIR_MAP", "=" * 30)
for i, ln in enumerate(lines, 1):
    if "_STAGE_DIR_MAP" in ln:
        for j in range(i-2, min(len(lines), i+8)):
            print(f"{j+1:4d}| {lines[j]}")
        print("-" * 60)

print()
print("=" * 30, "PROGRAM_GATES", "=" * 30)
for i, ln in enumerate(lines, 1):
    if "PROGRAM_GATES" in ln:
        for j in range(i-1, min(len(lines), i+8)):
            print(f"{j+1:4d}| {lines[j]}")
        break

print()
print("=" * 30, "mode 处理（human / storage / fixed）", "=" * 30)
for i, ln in enumerate(lines, 1):
    if 'mode") ==' in ln or "mode' ==" in ln or 'get("mode")' in ln:
        print(f"{i:4d}| {ln[:130]}")