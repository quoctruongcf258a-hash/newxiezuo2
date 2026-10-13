import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")

import tasks
print("=== tasks.py 导入成功 ===")

# 模拟一次产出
app = {"key": "doubao", "label": "豆包", "form": "desktop", "target": "x.exe"}
prompt_text = "你是写手，请根据上游资料写一份全书结构规划"
input_text = "F:\\...\\项目信息.json\nF:\\...\\用户输入.md"
extra_note = "一行一个字段：三幕划分 / 主线弧光 / 开局钩子"
out_path = "F:\\...\\全书结构__doubao.md"

result = tasks._file_mode_task(app, prompt_text, input_text, extra_note,
                                out_path, "规划", "全书结构", "produce")
print()
print("=== 外层 prompt（CDP 实际发送的）===")
print(result)

# 找生成的 task file，看内容
print()
print("=== 任务文件内容 ===")
import glob, os
task_files = sorted(Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files").glob("task__*.md"),
                     key=os.path.getmtime)
if task_files:
    latest = task_files[-1]
    print(f"📄 {latest.name}")
    print(latest.read_text(encoding="utf-8"))
