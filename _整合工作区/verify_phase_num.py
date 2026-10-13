import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)
import inspect

print("=" * 60)
print("环节编号补丁验证")
print("=" * 60)

print(f"  _fmt_phase_label 存在：{'✅' if hasattr(orchestrator, '_fmt_phase_label') else '❌'}")

# 测试函数
print()
print("[测试] _fmt_phase_label 输出：")
tests = [
    {"key": "一句话故事", "_idx": 4, "_total": 33},
    {"key": "文风与叙事基调", "_idx": 2, "_total": 33},
    {"key": "全书结构"},  # 无 idx
]
for tc in tests:
    print(f"    {orchestrator._fmt_phase_label('规划', tc)}")

# 检查 run_program 循环
src = inspect.getsource(orchestrator.run_program)
print()
print(f"  run_program 含 _idx：{'✅' if '_idx, ph in enumerate' in src else '❌'}")

# 检查 label 构造已替换
src2 = inspect.getsource(orchestrator.do_produce)
print(f"  do_produce 用 _fmt_phase_label：{'✅' if '_fmt_phase_label' in src2 else '❌'}")
