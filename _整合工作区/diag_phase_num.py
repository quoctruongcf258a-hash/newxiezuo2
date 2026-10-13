from pathlib import Path
import re

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

print("=" * 70)
print("① run_program 里的环节循环")
print("=" * 70)
m = re.search(r"def run_program\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    for i, ln in enumerate(body.splitlines(), 1):
        if "for ph in" in ln or "for " in ln and "phases" in ln or "run_mesh_phase" in ln:
            print(f"  {i:4d}| {ln.strip()[:120]}")

print()
print("=" * 70)
print("② phase_label 的构造点（所有 label = f... ）")
print("=" * 70)
for i, ln in enumerate(text.splitlines(), 1):
    if 'label = f"' in ln or "label=f\"" in ln:
        if "program" in ln or "phase" in ln:
            print(f"  {i:4d}| {ln.strip()[:130]}")

print()
print("=" * 70)
print("③ run_mesh_phase 开头")
print("=" * 70)
m = re.search(r"def run_mesh_phase\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    for i, ln in enumerate(m.group(0).splitlines()[:40], 1):
        print(f"  {i:4d}| {ln}")
