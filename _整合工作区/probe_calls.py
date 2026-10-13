# probe_calls.py — 找 keywords_for_phase / _upstream_files 的调用处
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "keywords_for_phase 调用处", "=" * 30)
for i, ln in enumerate(lines, 1):
    if "keywords_for_phase(" in ln and "def keywords_for_phase" not in ln:
        for j in range(max(0, i-3), min(len(lines), i+15)):
            print(f"{j+1:4d}| {lines[j]}")
        print("-" * 60)

print()
print("=" * 30, "_upstream_files 调用处", "=" * 30)
for i, ln in enumerate(lines, 1):
    if "_upstream_files(" in ln and "def _upstream_files" not in ln:
        for j in range(max(0, i-3), min(len(lines), i+20)):
            print(f"{j+1:4d}| {lines[j]}")
        print("-" * 60)

print()
print("=" * 30, "所有含 '前 10' / '[:10]' / '10]' 的行", "=" * 30)
for i, ln in enumerate(lines, 1):
    if "[:10]" in ln or "前 10" in ln or "[: 10]" in ln:
        print(f"{i:4d}| {ln}")