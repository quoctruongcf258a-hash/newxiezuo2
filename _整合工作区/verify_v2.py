import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator

print("=== import 成功 ===")
for fn in ["_run_task_stage", "_do_review_batch", "_do_merge_batch",
           "_do_modify_single", "_run_batch_mesh"]:
    ok = hasattr(orchestrator, fn)
    print(f"  {fn}: {'[OK]' if ok else '[FAIL]'}")

import inspect
src = inspect.getsource(orchestrator.run_mesh_phase)
print(f"\n  run_mesh_phase 含批量分支：{'是' if '_run_batch_mesh' in src else '否'}")
