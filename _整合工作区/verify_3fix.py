import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)
import inspect

print("=" * 60)
print("3 个补丁验证")
print("=" * 60)

# 修 1
src1 = inspect.getsource(orchestrator._do_produce_batch)
print(f"[1] verify_fn 用目录隔离：{'✅' if '_versions_dir / _ai /' in src1 or '_ai_dir = _versions_dir / _ai' in src1 else '❌'}")
print(f"    verify_fn 非空校验 ≥200：{'✅' if 'st_size >= 200' in src1 else '❌'}")

# 修 2
src2 = inspect.getsource(orchestrator.do_review)
print(f"[2] do_review 失败返回 None：{'✅' if 'return None' in src2 else '❌'}")

# 修 3
print(f"[3] _clean_old_named_files 存在：{'✅' if hasattr(orchestrator, '_clean_old_named_files') else '❌'}")
src3 = inspect.getsource(orchestrator._run_batch_mesh)
print(f"    _run_batch_mesh 调用清理：{'✅' if '_clean_old_named_files' in src3 else '❌'}")
