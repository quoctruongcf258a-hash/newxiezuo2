import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 70)
print("① run_mesh_phase 是否含批量分支")
print("=" * 70)
src = inspect.getsource(orchestrator.run_mesh_phase)
print(f"  含 _run_batch_mesh 调用：{'✅' if '_run_batch_mesh' in src else '❌'}")
print(f"  含 do_review 调用：{'✅' if 'do_review(' in src else '❌'}")
print(f"  含 _do_review_batch 调用：{'✅' if '_do_review_batch' in src else '❌'}")

print()
print("=" * 70)
print("② run_mesh_phase 前 30 行（看流程走向）")
print("=" * 70)
lines = src.splitlines()
for i, ln in enumerate(lines[:40]):
    print(f"  {i+1:3d}| {ln}")

print()
print("=" * 70)
print("③ _do_review_batch 是否真的调 _run_task_stage")
print("=" * 70)
src2 = inspect.getsource(orchestrator._do_review_batch)
print(f"  含 _run_task_stage：{'✅' if '_run_task_stage' in src2 else '❌'}")
print(f"  含 capture_with_meta：{'✅' if 'capture_with_meta' in src2 else '❌'}")

print()
print("=" * 70)
print("④ is_ai_busy / wait_idle 现在的位置")
print("=" * 70)
for name in ["_judge_task_status", "_run_task_stage", "_send_batch_task", "_do_produce_batch"]:
    fn = getattr(orchestrator, name, None)
    if fn:
        s = inspect.getsource(fn)
        has_busy = "is_ai_busy" in s
        has_idle = "wait_idle" in s
        print(f"  {name:25}  is_ai_busy={has_busy}  wait_idle={has_idle}")
