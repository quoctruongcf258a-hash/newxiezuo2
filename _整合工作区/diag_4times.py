from pathlib import Path
import re

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

print("=" * 70)
print("[1] run_mesh_phase 里的批量短路——有没有 return")
print("=" * 70)
m = re.search(r"def run_mesh_phase\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    # 找批量短路段
    i = body.find("_run_batch_mesh(")
    if i >= 0:
        print(body[i-500:i+300])

print()
print("=" * 70)
print("[2] run_program 里的环节循环——有没有 continue")
print("=" * 70)
m = re.search(r"def run_program\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    for i, ln in enumerate(body.splitlines(), 1):
        if any(k in ln for k in ["for ", "run_mesh_phase", "run_gate", "continue", "return", "break"]):
            print(f"  {i:4d}| {ln.strip()[:120]}")

print()
print("=" * 70)
print("[3] _do_produce_batch 的双层循环")
print("=" * 70)
m = re.search(r"def _do_produce_batch\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    for i, ln in enumerate(body.splitlines(), 1):
        if any(k in ln for k in ["for ai_idx", "for attempt", "break", "continue", "return out_files", "return []"]):
            print(f"  {i:4d}| {ln}")
