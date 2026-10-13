from pathlib import Path
import re

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

print("=" * 70)
print("[1] _do_produce_batch 的 verify_fn")
print("=" * 70)
m = re.search(r"def _do_produce_batch\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    i = body.find("def verify_fn")
    if i >= 0:
        print(body[i:i+800])

print()
print("=" * 70)
print("[2] _do_review_batch 的 verify_fn")
print("=" * 70)
m = re.search(r"def _do_review_batch\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    i = body.find("def verify_fn")
    if i >= 0:
        print(body[i:i+800])

print()
print("=" * 70)
print("[3] do_review 里未抓到回复的处理")
print("=" * 70)
m = re.search(r"def do_review\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    for i, ln in enumerate(body.splitlines(), 1):
        if "未抓到" in ln or "return" in ln:
            print(f"  {i:4d}| {ln.strip()[:120]}")

print()
print("=" * 70)
print("[4] 旧文件清理逻辑")
print("=" * 70)
for i, ln in enumerate(text.splitlines(), 1):
    s = ln.strip()
    if s.startswith("def ") and ("clean" in s.lower() or "清理" in s):
        print(f"  {i:4d}| {s}")
for i, ln in enumerate(text.splitlines(), 1):
    if "unlink()" in ln and ("versions" in ln or "旧" in ln or "rglob" in ln):
        print(f"  {i:4d}| {ln.strip()[:120]}")
