import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 70)
print("[1] do_produce 里的分支（走批量 vs 通用）")
print("=" * 70)
src = inspect.getsource(orchestrator.do_produce)
for i, ln in enumerate(src.splitlines(), 1):
    s = ln.strip()
    if any(k in s for k in ["_do_produce_batch", "_do_produce_renwu",
                             "_get_split_spec", "_do_produce_split",
                             "if _split_spec", "return _do_produce"]):
        print(f"  {i:4d}| {ln}")

print()
print("=" * 70)
print("[2] _run_batch_mesh 阶段1（真实代码）")
print("=" * 70)
src2 = inspect.getsource(orchestrator._run_batch_mesh)
lines = src2.splitlines()
in_stage1 = False
cnt = 0
for i, ln in enumerate(lines):
    if "阶段1" in ln:
        in_stage1 = True
    if in_stage1:
        print(f"  {i+1:4d}| {ln}")
        cnt += 1
        if cnt >= 40:
            break

print()
print("=" * 70)
print("[3] _do_produce_batch 里 ai_order 构造")
print("=" * 70)
src3 = inspect.getsource(orchestrator._do_produce_batch)
for i, ln in enumerate(src3.splitlines(), 1):
    s = ln.strip()
    if any(k in s for k in ["ai_order", "backup_keys", "_is_serial", "[赛马]", "[串行]", "for ai_idx"]):
        print(f"  {i:4d}| {ln}")
