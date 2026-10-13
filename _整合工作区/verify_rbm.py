import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)
import inspect

src = inspect.getsource(orchestrator._run_batch_mesh)
print("=" * 60)
print("_run_batch_mesh 串行/赛马判定")
print("=" * 60)
print(f"  含 is_serial_produce：{'✅' if 'is_serial_produce' in src else '❌'}")
print(f"  含 is_serial_review：{'✅' if 'is_serial_review' in src else '❌'}")
print(f"  含 sess['_is_serial_produce']：{'✅' if 'sess[\"_is_serial_produce\"]' in src or 'sess[' in src and '_is_serial_produce' in src else '❌'}")
print(f"  含 [模式] 打印：{'✅' if '[模式]' in src else '❌'}")
