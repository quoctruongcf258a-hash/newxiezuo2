import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator, tasks
importlib.reload(orchestrator)
importlib.reload(tasks)

print("=" * 60)
print("动态步骤分配验证")
print("=" * 60)

print(f"  _get_or_assign_step 存在：{'✅' if hasattr(orchestrator, '_get_or_assign_step') else '❌'}")

# 模拟分配
step1 = orchestrator._get_or_assign_step("doubao", "versions/doubao/全书结构.md")
print(f"\n  第 1 次分配（产出）：步骤 {step1}")

step2 = orchestrator._get_or_assign_step("doubao", "reviews/doubao/全书结构.json")
print(f"  第 2 次分配（盲审）：步骤 {step2}")

# 重发同一个任务
step3 = orchestrator._get_or_assign_step("doubao", "versions/doubao/全书结构.md")
print(f"  重发产出（应复用步骤 {step1}）：步骤 {step3}")

step4 = orchestrator._get_or_assign_step("doubao", "versions/doubao/分卷结构.md")
print(f"  下个环节（P10 产出）：步骤 {step4}")
