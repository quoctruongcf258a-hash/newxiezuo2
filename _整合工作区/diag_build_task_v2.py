import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 70)
print("_do_produce_batch 里的 build_task")
print("=" * 70)
src = inspect.getsource(orchestrator._do_produce_batch)
i = src.find("def build_task")
if i >= 0:
    print(src[i:i+800])

print()
print("=" * 70)
print("_do_produce_batch 里调用 build_produce_task 的地方")
print("=" * 70)
for i, ln in enumerate(src.splitlines(), 1):
    if "build_produce_task" in ln or "tasks_mod.build" in ln:
        print(f"  {i:4d}| {ln}")

print()
print("=" * 70)
print("_do_review_batch 里的 build_task 和 build_review_task")
print("=" * 70)
src2 = inspect.getsource(orchestrator._do_review_batch)
i = src2.find("def build_task")
if i >= 0:
    print(src2[i:i+800])
