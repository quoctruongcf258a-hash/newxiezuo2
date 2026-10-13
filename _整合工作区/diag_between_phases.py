from pathlib import Path
import re

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

print("=" * 70)
print("① run_program 里的环节循环逻辑")
print("=" * 70)
m = re.search(r"def run_program\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    lines = body.splitlines()
    for i, ln in enumerate(lines):
        stripped = ln.strip()
        # 只关心：循环、等待、sleep、gate、phase 切换
        if any(k in stripped for k in ["for ph", "run_mesh_phase", "run_gate", 
                                        "time.sleep", "continue", "pass", 
                                        "candidate", "输出闸", "GATE", "phase"]):
            print(f"  {i+1:4d}| {ln}")

print()
print("=" * 70)
print("② 有没有环节间的 sleep / 等待")
print("=" * 70)
for i, ln in enumerate(text.splitlines(), 1):
    if "time.sleep" in ln:
        # 打印上下文 3 行
        start = max(0, i-3)
        end = min(len(text.splitlines()), i+2)
        for j in range(start, end):
            print(f"  {j+1:4d}| {text.splitlines()[j]}")
        print("  " + "-"*50)

print()
print("=" * 70)
print("③ 有没有「等所有 AI 空闲再进下一环」的逻辑")
print("=" * 70)
for i, ln in enumerate(text.splitlines(), 1):
    if "wait_idle" in ln or "wait_all_idle" in ln or "等所有" in ln or "都空闲" in ln:
        print(f"  {i:4d}| {ln.strip()[:120]}")

print()
print("=" * 70)
print("④ run_gate（出口闸）调用点")
print("=" * 70)
for i, ln in enumerate(text.splitlines(), 1):
    if "run_gate(" in ln and "def " not in ln:
        start = max(0, i-5)
        end = min(len(text.splitlines()), i+3)
        for j in range(start, end):
            print(f"  {j+1:4d}| {text.splitlines()[j]}")
        print("  " + "-"*50)
