import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator, tasks
importlib.reload(orchestrator)
importlib.reload(tasks)

print("=" * 60)
print("动态步骤号验证")
print("=" * 60)

print(f"  _get_or_assign_step 存在：{'✅' if hasattr(orchestrator, '_get_or_assign_step') else '❌'}")

# 模拟分配
s1 = orchestrator._get_or_assign_step("doubao", "versions/doubao/全书结构.md")
print(f"\n  第 1 次分配（产出）：步骤 {s1}")

s2 = orchestrator._get_or_assign_step("doubao", "reviews/doubao/全书结构.json")
print(f"  第 2 次分配（盲审）：步骤 {s2}")

# 重发同一个任务
s3 = orchestrator._get_or_assign_step("doubao", "versions/doubao/全书结构.md")
print(f"  重发产出（应复用步骤 {s1}）：步骤 {s3}")

s4 = orchestrator._get_or_assign_step("doubao", "versions/doubao/分卷结构.md")
print(f"  下个环节（P10 产出）：步骤 {s4}")

# 测试 _file_mode_task 生成
print()
print("=" * 60)
print("测试 _file_mode_task 生成的 prompt")
print("=" * 60)
app = {"key": "doubao", "label": "Doubao", "form": "desktop", "target": "x.exe"}
result = tasks._file_mode_task(
    app, "你是写手", "资料路径", "格式要求",
    "F:\\test\\out2.md", "规划 › 环节1/33 全书结构", "全书结构", "produce"
)
print(result)
