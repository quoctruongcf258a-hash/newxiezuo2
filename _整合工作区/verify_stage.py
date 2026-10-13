import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

# 检查 4/5/6
src2 = inspect.getsource(orchestrator._do_review_batch)
print(f"_do_review_batch 含 _is_serial_r：{'✅' if '_is_serial_r' in src2 else '❌'}")
print(f"_do_review_batch 含 backup_keys = []：{'✅' if 'backup_keys = []' in src2 else '❌'}")
