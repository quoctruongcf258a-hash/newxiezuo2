import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 70)
print("_do_review_batch 完整代码")
print("=" * 70)
print(inspect.getsource(orchestrator._do_review_batch))

print()
print("=" * 70)
print("_run_task_stage 是否含 do_review 调用")
print("=" * 70)
src = inspect.getsource(orchestrator._run_task_stage)
print(f"  含 do_review：{'✅' if 'do_review' in src else '❌'}")
print(f"  含 capture_with_meta：{'✅' if 'capture_with_meta' in src else '❌'}")
