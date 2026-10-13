import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 70)
print("_run_batch_mesh 的【阶段2：盲审】代码")
print("=" * 70)
src = inspect.getsource(orchestrator._run_batch_mesh)
i = src.find("阶段2")
if i >= 0:
    print(src[i:i+1500])

print()
print("=" * 70)
print("_do_review_batch 用的是什么函数（是新还是旧）")
print("=" * 70)
src2 = inspect.getsource(orchestrator._do_review_batch)
print(f"  含 _run_task_stage：{'✅' if '_run_task_stage' in src2 else '❌'}")
print(f"  含 do_review：{'✅' if 'do_review(' in src2 else '❌'}")
print(f"  含 capture_with_meta：{'✅' if 'capture_with_meta' in src2 else '❌'}")
