import sys, importlib
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")

import tasks
importlib.reload(tasks)
import inspect

sig = inspect.signature(tasks._write_task_file)
print(f"[1] _write_task_file 签名：")
print(f"    {sig}")
print(f"    含 ai_key 参数：{'✅' if 'ai_key' in sig.parameters else '❌'}")

print(f"\n[2] 并发写 4 个任务文件")
files = []
for ai in ["workbuddy", "doubao", "codebuddy", "gemini"]:
    f = tasks._write_task_file(
        f"你是 {ai}，请执行任务",
        "上游资料路径",
        "格式要求",
        "测试环节",
        "测试块",
        f"F:\\test\\{ai}.md",
        "produce",
        ai_key=ai,
    )
    files.append(f)

for f in files:
    print(f"    {f.name}")

if len(set(files)) == len(files):
    print(f"\n    ✅ 4 个文件路径都不同")
else:
    print(f"\n    ❌ 有重复！")

print(f"\n[3] 第 1 个文件的内容（前 200 字）")
print(files[0].read_text(encoding="utf-8")[:200])
