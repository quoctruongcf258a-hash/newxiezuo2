import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator, tasks
importlib.reload(orchestrator)
importlib.reload(tasks)
import inspect

print("=" * 60)
print("进度显示补丁验证")
print("=" * 60)

# 1. _scan_progress 存在
print(f"  _scan_progress 存在：{'✅' if hasattr(orchestrator, '_scan_progress') else '❌'}")

# 2. _wait_ai_task_done 加参数
sig = inspect.signature(orchestrator._wait_ai_task_done)
print(f"  _wait_ai_task_done 有 _progress_items：{'✅' if '_progress_items' in sig.parameters else '❌'}")

# 3. 函数体里有进度打印
src = inspect.getsource(orchestrator._wait_ai_task_done)
print(f"  含 📊 进度打印：{'✅' if '📊 进度' in src else '❌'}")

# 4. tasks.py 回复格式
src2 = inspect.getsource(tasks._file_mode_task)
print(f"  tasks.py 回复带文件清单：{'✅' if '生成文件列表' in src2 else '❌'}")

# 5. 测试 _scan_progress
print()
print("[测试] _scan_progress（模拟空目录）：")
done, total = orchestrator._scan_progress("workbuddy", ["章1", "章2", "章3"], "/tmp/test")
print(f"    {done}/{total}")
