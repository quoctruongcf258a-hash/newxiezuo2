import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 70)
print("run_mesh_phase 的短路代码")
print("=" * 70)
src = inspect.getsource(orchestrator.run_mesh_phase)
i = src.find("批量")
if i < 0:
    i = src.find("_batch_split_spec")
if i >= 0:
    print(src[i:i+800])

print()
print("=" * 70)
print("SPLIT_PRODUCERS 内容")
print("=" * 70)
print(orchestrator.SPLIT_PRODUCERS)
