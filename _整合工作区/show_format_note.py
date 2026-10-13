# show_format_note.py — 看 format_note 的前 60 行 + 所有调用点
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

# 1) 找 def format_note
start = None
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("def format_note"):
        start = i
        break

print("=" * 30, "format_note 定义", "=" * 30)
if start is None:
    print("没找到 def format_note")
else:
    # 打到下一个 def 或顶格代码
    end = start + 1
    while end < len(lines):
        ln = lines[end]
        if ln.lstrip().startswith("def ") and not ln.startswith(" " * 8):
            break
        if ln.startswith("def "):
            break
        end += 1
        if end - start > 80:
            break
    for i in range(start, min(end, start + 60)):
        print(f"{i+1:4d}| {lines[i]}")

# 2) 找所有 format_note( 调用点
print()
print("=" * 30, "调用点", "=" * 30)
for i, ln in enumerate(lines):
    if "format_note(" in ln and "def format_note" not in ln:
        print(f"{i+1:4d}| {ln}")

# 3) 找 phase_cfg 是怎么来的（do_produce 里）
print()
print("=" * 30, "phase_cfg 装载点", "=" * 30)
for i, ln in enumerate(lines):
    if "rings_items" in ln or "_load_phases" in ln or "load_rings" in ln:
        print(f"{i+1:4d}| {ln}")