import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")

import tasks
importlib.reload(tasks)

# 模拟生成一个任务文件
app = {"key": "workbuddy", "label": "WorkBuddy", "form": "desktop", "target": "x.exe"}
task_file = tasks._file_mode_task(
    app,
    "你是写手，请写全书结构",
    "上游资料路径",
    "格式要求",
    "F:\\test\\versions\\workbuddy\\全书结构.md",
    "规划 › 全书结构",
    "全书结构",
    "produce",
)
print("=" * 70)
print("外层 prompt（CDP 实际发送的）")
print("=" * 70)
print(task_file)
print()
print("=" * 70)
print("任务文件内容（前 800 字）")
print("=" * 70)
# 找最新生成的任务文件
import os
task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
files = sorted(task_dir.glob("task__*.md"), key=os.path.getmtime)
if files:
    latest = files[-1]
    print(f"📄 {latest.name}")
    print(latest.read_text(encoding="utf-8")[:800])
