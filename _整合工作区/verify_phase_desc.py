from pathlib import Path
import os

task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")

# 清旧任务文件
cnt = 0
for f in task_dir.glob("task__*.md"):
    f.unlink()
    cnt += 1
print(f"已删除 {cnt} 个旧任务文件")

# 模拟一次产出
import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import importlib
import orchestrator
importlib.reload(orchestrator)

# 直接用 tasks 模块测
import tasks

app = {"key": "doubao", "label": "豆包", "form": "desktop", "target": "x.exe"}
# 模拟注入后的 tpl
phase_desc = "每章一句话（约30字），按卷分次产出"
phase_name = "简短细纲规划"
header = f"# 本环节：{phase_name}\n\n## 本环节任务说明\n{phase_desc}\n\n## 以下是通用写作要求\n\n"
tpl = header + "（此处是通用模板内容...）"

task_file = tasks._write_task_file(tpl, "F:\\...\\项目信息.json", "一行一个字段",
                                    "规划", phase_name, "F:\\...\\out.md", "produce")
print(f"\n生成任务文件：{task_file.name}")
print("=" * 70)
print(task_file.read_text(encoding="utf-8")[:1500])
