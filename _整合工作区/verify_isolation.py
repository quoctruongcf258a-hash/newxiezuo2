import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 60)
print("统一隔离检查")
print("=" * 60)

# run_mesh_phase 短路
src = inspect.getsource(orchestrator.run_mesh_phase)
print(f"  run_mesh_phase:")
print(f"    含 _run_batch_mesh：{'✅' if '_run_batch_mesh' in src else '❌'}")
print(f"    短路条件：{'所有非人物设计' if '人物设计' in src and '_phase_name_now' in src else '需检查'}")

# do_produce 用 ai_dir
src2 = inspect.getsource(orchestrator.do_produce)
print(f"  do_produce:")
print(f"    用 ai_dir 目录：{'✅' if 'versions\" / app[\"key\"]' in src2 or '/ app[\"key\"]' in src2 else '❌'}")

# do_review 用 ai_dir
src3 = inspect.getsource(orchestrator.do_review)
print(f"  do_review:")
print(f"    用 ai_dir 目录：{'✅' if 'reviews\" / app[\"key\"]' in src3 else '❌'}")

# _do_produce_split 用 ai_dir
src4 = inspect.getsource(orchestrator._do_produce_split)
print(f"  _do_produce_split:")
print(f"    用 ai_dir 目录：{'✅' if 'versions\" / app[\"key\"]' in src4 else '❌'}")
