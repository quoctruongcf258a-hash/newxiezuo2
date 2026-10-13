import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''    return (
        f"请读取文件：{task_file}\\n"
        f"按文件里「## 你的任务」章节的要求执行。\\n"
        f"完成后，按文件里「## 输出位置」章节的路径保存结果。\\n"
        f"回复「✅ 已完成」即可，不要输出多余说明。"
    )'''

NEW = '''    _out_name = Path(out_path).name
    _ai = app.get("key") or "unknown"
    return (
        f"请读取文件：{task_file}\\n"
        f"按文件里「## 你的任务」章节的要求执行。\\n"
        f"完成后，按文件里「## 输出位置」章节的路径保存结果。\\n"
        f"最后**必须**回复这一行（一字不改）：\\n"
        f"  ✅ [{_ai}] {phase_label} → {_out_name} 已完成\\n"
        f"不要输出多余说明。"
    )'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] 已改 _file_mode_task 的外层 prompt")
else:
    print("[FAIL] 找不到锚点")
    i = text.find("回复「✅ 已完成」即可")
    if i >= 0:
        print("\n附近代码：")
        print(text[max(0,i-300):i+200])

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 已写回")
