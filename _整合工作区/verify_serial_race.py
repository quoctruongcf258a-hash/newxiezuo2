import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 60)
print("串行/赛马判定检查")
print("=" * 60)

src1 = inspect.getsource(orchestrator._run_batch_mesh)
print(f"  _run_batch_mesh:")
print(f"    含 _is_serial_produce：{'✅' if '_is_serial_produce' in src1 else '❌'}")
print(f"    含 _is_serial_review：{'✅' if '_is_serial_review' in src1 else '❌'}")
print(f"    含 [模式] 打印：{'✅' if '[模式]' in src1 else '❌'}")

src2 = inspect.getsource(orchestrator._do_produce_batch)
print(f"  _do_produce_batch:")
print(f"    含 _is_serial 判断：{'✅' if '_is_serial' in src2 else '❌'}")
print(f"    含 [串行]/[赛马] 打印：{'✅' if '[串行]' in src2 or '[赛马]' in src2 else '❌'}")

src3 = inspect.getsource(orchestrator._do_review_batch)
print(f"  _do_review_batch:")
print(f"    含 _is_serial_r：{'✅' if '_is_serial_r' in src3 else '❌'}")
