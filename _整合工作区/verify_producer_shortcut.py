import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)
import inspect

print("=" * 60)
print("生产者短路补丁验证")
print("=" * 60)

src = inspect.getsource(orchestrator.run_mesh_phase)
print(f"  含生产者判断：{'✅' if 'SPLIT_PRODUCERS' in src else '❌'}")
print(f"  含 [短路] 打印：{'✅' if '[短路]' in src else '❌'}")

src2 = inspect.getsource(orchestrator._do_review_batch)
print(f"  盲审输出 .json：{'✅' if '全书结构.json' in src2 else '❌'}")
