import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)
import inspect

src = inspect.getsource(orchestrator._run_batch_mesh)
print(f"_run_batch_mesh 调清理：{'✅' if '_clean_old_named_files' in src else '❌'}")

# 打印前 20 行确认
print()
print("=== _run_batch_mesh 前 20 行 ===")
for i, ln in enumerate(src.splitlines()[:20], 1):
    print(f"  {i:3d}| {ln}")
