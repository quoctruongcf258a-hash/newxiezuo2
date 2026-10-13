# fix_extract.py — _extract_prompt 识别文件模式，不要截取
import shutil
from pathlib import Path

ORCH = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = ORCH.read_text(encoding="utf-8")

OLD = '''def _extract_prompt(task_text):
    """从 SOP 里抠出『指令开始...指令结束』之间的正文。"""
    i = task_text.find("===== 指令开始 =====")
    j = task_text.find("===== 指令结束 =====")
    if i >= 0 and j > i:
        return task_text[i + len("===== 指令开始 ====="):j].strip()
    return task_text
'''

NEW = '''def _extract_prompt(task_text):
    """从 SOP 里抠出『指令开始...指令结束』之间的正文。

    文件模式（含 _task_files 路径）不走截取——整个 task 都是要发给 AI 的指令。
    """
    # 文件模式：整个 task 就是指令，不截取
    if "_task_files" in task_text:
        return task_text
    i = task_text.find("===== 指令开始 =====")
    j = task_text.find("===== 指令结束 =====")
    if i >= 0 and j > i:
        return task_text[i + len("===== 指令开始 ====="):j].strip()
    return task_text
'''

if "文件模式（含 _task_files 路径）不走截取" in text:
    print("已改过")
elif OLD not in text:
    print("找不到 _extract_prompt")
else:
    bak = ORCH.with_suffix(".py.bak_extract")
    if not bak.exists():
        shutil.copy(ORCH, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    ORCH.write_text(text, encoding="utf-8")
    print("✔ _extract_prompt 已修：文件模式不截取")