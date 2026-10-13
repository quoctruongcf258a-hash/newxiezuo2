from pathlib import Path
import re

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

print("=" * 70)
print("所有「输出文件路径」拼接点")
print("=" * 70)

# 找所有包含 out_dir / versions / reviews / merged 的路径拼接
patterns = [
    "versions",
    "reviews",
    "merged",
]

for i, ln in enumerate(text.splitlines(), 1):
    stripped = ln.strip()
    # 只关心路径拼接相关
    if any(p in stripped for p in patterns):
        if "/" in stripped and ("out_dir" in stripped or "out" in stripped or "ai_dir" in stripped or "review_dir" in stripped or "merged_dir" in stripped):
            print(f"  {i:4d}| {stripped[:130]}")

print()
print("=" * 70)
print("① do_produce（旧）的输出路径")
print("=" * 70)
m = re.search(r"def do_produce\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    for ln in body.splitlines():
        if "out = " in ln or "versions" in ln:
            print(f"  {ln.strip()[:120]}")

print()
print("=" * 70)
print("② _do_produce_split（旧）的输出路径")
print("=" * 70)
m = re.search(r"def _do_produce_split\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    for ln in body.splitlines():
        if "out = " in ln or "versions" in ln:
            print(f"  {ln.strip()[:120]}")

print()
print("=" * 70)
print("③ do_review（旧）的输出路径")
print("=" * 70)
m = re.search(r"def do_review\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    for ln in body.splitlines():
        if "out = " in ln or "reviews" in ln:
            print(f"  {ln.strip()[:120]}")

print()
print("=" * 70)
print("④ do_merge（旧）的输出路径")
print("=" * 70)
m = re.search(r"def do_merge\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    for ln in body.splitlines():
        if "out = " in ln or "merged" in ln:
            print(f"  {ln.strip()[:120]}")

print()
print("=" * 70)
print("⑤ 新函数 _do_produce_batch / _do_review_batch / _do_merge_batch")
print("=" * 70)
for fn in ["_do_produce_batch", "_do_review_batch", "_do_merge_batch", "_do_modify_single"]:
    m = re.search(rf"def {fn}\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
    if m:
        body = m.group(0)
        print(f"\n--- {fn} ---")
        for ln in body.splitlines():
            if "ai_dir" in ln or "review_dir" in ln or "merged_dir" in ln or "/ versions" in ln or "/ reviews" in ln or "/ merged" in ln:
                print(f"  {ln.strip()[:120]}")
