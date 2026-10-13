import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import importlib
import orchestrator
importlib.reload(orchestrator)

print("=== import 成功 ===")
import inspect

# 检查 _build_batch_prompt 的路径拼接
src = inspect.getsource(orchestrator._build_batch_prompt)
print(f"  _build_batch_prompt 用 <versions>/<ai>/：{'是' if 'versions\" / ai_key' in src or chr(39)+'versions'+chr(39)+' / ai_key' in src or 'versions / ai_key' in src else '否'}")

# 检查 _do_produce_batch 里的 verify_fn
src2 = inspect.getsource(orchestrator._do_produce_batch)
print(f"  _do_produce_batch 用 <versions>/<ai>/：{'是' if 'ai_dir = _versions_dir / _ai' in src2 else '否'}")
