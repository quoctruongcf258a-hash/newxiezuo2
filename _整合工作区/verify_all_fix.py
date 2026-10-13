import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)
import inspect

print("=" * 60)
print("补丁验证")
print("=" * 60)

# 1. do_produce 判断生产者
src1 = inspect.getsource(orchestrator.do_produce)
print(f"  do_produce 判断 SPLIT_PRODUCERS：{'✅' if 'SPLIT_PRODUCERS' in src1 else '❌'}")

# 2. _build_batch_prompt 目录隔离
src2 = inspect.getsource(orchestrator._build_batch_prompt)
print(f"  _build_batch_prompt 用 ai_dir：{'✅' if 'ai_dir = Path(out_dir)' in src2 else '❌'}")
print(f"  _build_batch_prompt 用 item_key 作文件名：{'✅' if 'ai_dir / f\"{safe}.md\"' in src2 else '❌'}")

# 3. phase_input 旧路径已删
src3 = inspect.getsource(orchestrator.phase_input)
print(f"  phase_input 旧路径已删：{'✅' if '本环节输出路径' not in src3 else '❌ 未删'}")
