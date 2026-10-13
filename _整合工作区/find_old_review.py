from pathlib import Path

T = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = T.read_text(encoding="utf-8")

print("=" * 70)
print("orchestrator.py 里所有 do_review( 调用点")
print("=" * 70)
for i, ln in enumerate(text.splitlines(), 1):
    if "do_review(" in ln and "def " not in ln and "。" not in ln:
        print(f"  {i:5d}| {ln.strip()[:130]}")

print()
print("=" * 70)
print("orchestrator.py 里所有 build_review_task 调用点")
print("=" * 70)
for i, ln in enumerate(text.splitlines(), 1):
    if "build_review_task" in ln and "def " not in ln:
        print(f"  {i:5d}| {ln.strip()[:130]}")

print()
print("=" * 70)
print("orchestrator.py 里 _do_review_batch 调用点")
print("=" * 70)
for i, ln in enumerate(text.splitlines(), 1):
    if "_do_review_batch(" in ln and "def " not in ln:
        print(f"  {i:5d}| {ln.strip()[:130]}")
