import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)
import inspect

src = inspect.getsource(orchestrator._run_batch_mesh)
print("=" * 60)
print("_run_batch_mesh 阶段1 检查")
print("=" * 60)

has_produce_one = "_produce_one" in src
has_sess_sub = "_sess_sub" in src
has_sub_participants = "_sess_sub[participants]" in src.replace('"', '').replace("'", "")

print(f"  含 _produce_one：{'✅' if has_produce_one else '❌'}")
print(f"  含 _sess_sub：{'✅' if has_sess_sub else '❌'}")
print(f"  含只传当前 writer：{'✅' if has_sub_participants else '❌'}")

# 打印阶段1前 30 行
print()
print("=== 阶段1 前 30 行 ===")
lines = src.splitlines()
in_stage = False
cnt = 0
for i, ln in enumerate(lines):
    if "阶段1：产出" in ln:
        in_stage = True
    if in_stage:
        print(f"  {i+1:3d}| {ln}")
        cnt += 1
        if cnt >= 30:
            break
