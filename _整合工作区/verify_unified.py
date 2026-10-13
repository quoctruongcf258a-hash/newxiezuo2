import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 70)
print("忙闲监控接入检查")
print("=" * 70)

# 1. 通用函数存在
print(f"  _wait_ai_task_done: {'✅' if hasattr(orchestrator, '_wait_ai_task_done') else '❌'}")

# 2. 各处调用
for fn in ["_run_task_stage", "_do_produce_batch"]:
    f = getattr(orchestrator, fn, None)
    if f:
        src = inspect.getsource(f)
        print(f"  {fn}:")
        print(f"    含 _wait_ai_task_done：{'✅' if '_wait_ai_task_done' in src else '❌'}")
        print(f"    含 wait_idle（前置）：{'✅' if 'wait_idle' in src else '❌'}")

# 3. run_task 的校验
src = inspect.getsource(orchestrator.run_task)
print(f"  run_task:")
print(f"    含忙闲轮询：{'✅' if 'is_ai_busy' in src and 'for _i in range(10)' in src else '❌'}")
