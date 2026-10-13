import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

# 改外层 prompt
OLD = '''    _out_name = Path(out_path).name
    _ai = app.get("key") or "unknown"
    return (
        f"请读取文件：{task_file}\\n"
        f"按文件里「## 你的任务」章节的要求执行。\\n"
        f"完成后，按文件里「## 输出位置」章节的路径保存结果。\\n"
        f"最后**必须**回复这一行（一字不改）：\\n"
        f"  ✅ [{_ai}] {phase_label} → {_out_name} 已完成\\n"
        f"不要输出多余说明。"
    )'''

NEW = '''    _ai = app.get("key") or "unknown"
    return (
        f"请读取文件：{task_file}\\n"
        f"按文件里「## 你的任务」章节的要求执行。\\n"
        f"完成后，按文件里「## 输出位置」章节的路径保存结果。\\n"
        f"最后**必须**回复这一行（一字不改，注意带文件清单）：\\n"
        f"  ✅ [{_ai}] {phase_label} → <已完成数>/<总文件数> 已完成\\n"
        f"  生成文件列表：\\n"
        f"    - <文件名1>\\n"
        f"    - <文件名2>\\n"
        f"    - ...\\n"
        f"不要输出多余说明。"
    )'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] 改 _file_mode_task 外层 prompt")
else:
    print("[FAIL] 找不到外层 prompt 锚点")

# 改任务文件里的回复格式
OLD2 = '''    # 回复标识：带 ai_key + 环节名 + 输出文件名，便于肉眼确认哪个任务完成
    _out_name = Path(out_path).name
    body += f"- 完成后，**必须**回复这一行（一字不改）：\\n"
    body += f"  `✅ [{ai_key}] {phase_label} → {_out_name} 已完成`\\n"
    body += f"- 如果失败，回复 `❌ [{ai_key}] {phase_label} → {_out_name} 失败：<原因>`\\n"'''

NEW2 = '''    # 回复标识：带 ai_key + 环节名 + 文件进度
    body += f"- 完成后，**必须**回复这一行（一字不改，注意带文件清单）：\\n"
    body += f"  `✅ [{ai_key}] {phase_label} → <已完成数>/<总文件数> 已完成`\\n"
    body += f"  生成文件列表：\\n"
    body += f"    - <文件名1>\\n"
    body += f"    - <文件名2>\\n"
    body += f"    - ...\\n"
    body += f"- 如果失败，回复 `❌ [{ai_key}] {phase_label} 失败：<原因>`\\n"'''

cnt = text.count(OLD2)
if cnt > 0:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 改任务文件回复格式")
else:
    print("[WARN] 找不到任务文件回复锚点")

bak = TARGET.with_suffix(".py.bak_progress3")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")
TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 已写回")
