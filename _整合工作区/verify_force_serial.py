import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)
import inspect

print("=" * 60)
print("_force_serial 传参链")
print("=" * 60)

sig1 = inspect.signature(orchestrator.do_produce)
print(f"  do_produce 有 _force_serial：{'✅' if '_force_serial' in sig1.parameters else '❌'}")

sig2 = inspect.signature(orchestrator._do_produce_batch)
print(f"  _do_produce_batch 有 _force_serial：{'✅' if '_force_serial' in sig2.parameters else '❌'}")

src = inspect.getsource(orchestrator._run_batch_mesh)
print(f"  _run_batch_mesh 传 _force_serial：{'✅' if '_force_serial=is_serial_produce' in src else '❌'}")

src2 = inspect.getsource(orchestrator._do_produce_batch)
print(f"  读参优先级：{'✅' if '_force_serial is not None' in src2 else '❌'}")
print(f"  含 [判定] 打印：{'✅' if '[判定]' in src2 else '❌'}")
