import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)
import inspect

print("=" * 60)
print("累计进度补丁验证")
print("=" * 60)

print(f"  _scan_total_progress 存在：{'✅' if hasattr(orchestrator, '_scan_total_progress') else '❌'}")

src = inspect.getsource(orchestrator._wait_ai_task_done)
print(f"  _wait_ai_task_done 含 _prog_total：{'✅' if '_prog_total' in src else '❌'}")

src2 = inspect.getsource(orchestrator._do_produce_batch)
print(f"  _do_produce_batch 含 _prog_total：{'✅' if '_prog_total' in src2 else '❌'}")
