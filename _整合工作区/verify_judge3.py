import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator

import inspect
src = inspect.getsource(orchestrator._judge_task_status)
print("=== _judge_task_status 是否更新 ===")
print(f"  含 MIN_STARTUP: {'是' if 'MIN_STARTUP' in src else '否'}")
print(f"  含 _idle_count: {'是' if '_idle_count' in src else '否'}")
print(f"  含 is_ai_busy(ai_key)（旧写法）: {'是（未修）' if 'is_ai_busy(ai_key)' in src else '否（已修）'}")
