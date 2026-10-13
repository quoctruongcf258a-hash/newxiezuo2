# fix_open_instr2.py — target 为空时简化文案
from pathlib import Path

TASKS = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TASKS.read_text(encoding="utf-8")

OLD = '''        return (
            f"启动或聚焦「{label}」桌面程序（它在系统中的识别方式：{exe}）。"
            f"若已在运行，直接切换到其主窗口并置前；找不到就停下并报告不可用。"
        )'''

NEW = '''        if exe:
            return (
                f"启动或聚焦「{label}」桌面程序（它在系统中的识别方式：{exe}）。"
                f"若已在运行，直接切换到其主窗口并置前；找不到就停下并报告不可用。"
            )
        return (
            f"启动或聚焦「{label}」桌面程序。"
            f"若已在运行，直接切换到其主窗口并置前；找不到就停下并报告不可用。"
        )'''

if "if exe:\n            return (\n                f\"启动或聚焦" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
else:
    text = text.replace(OLD, NEW, 1)
    TASKS.write_text(text, encoding="utf-8")
    print("✔ 已修：target 为空时简化文案")