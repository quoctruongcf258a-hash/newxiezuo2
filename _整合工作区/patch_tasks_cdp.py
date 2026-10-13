import shutil
from pathlib import Path
import re

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_cdp_task")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# ── 1. 重写 _file_mode_task：极简外层 prompt ──
OLD_FILE_MODE = re.search(r"def _file_mode_task\(.*?(?=\n\nclass |\n\ndef |\Z)", text, re.DOTALL)
if OLD_FILE_MODE:
    NEW_FILE_MODE = '''def _file_mode_task(app, prompt_text, input_text, extra_note, out_path,
                    phase_label, chunk_label, kind):
    """CDP 直发模式：给 AI 极简指令——读任务文件、执行、写结果。
    AI 用文件读写能力自己完成，不需要 GUI 操作步骤。
    """
    task_file = _write_task_file(prompt_text, input_text, extra_note,
                                  phase_label, chunk_label, out_path, kind)
    _kind_label = {
        "produce": "产出",
        "review": "盲审",
        "merge": "拼接",
    }.get(kind, "任务")

    return (
        f"请读取文件：{task_file}\\n"
        f"按文件里「## 你的任务」章节的要求执行。\\n"
        f"完成后，按文件里「## 输出位置」章节的路径保存结果。\\n"
        f"回复「✅ 已完成」即可，不要输出多余说明。"
    )'''
    text = text[:OLD_FILE_MODE.start()] + NEW_FILE_MODE + text[OLD_FILE_MODE.end():]
    print("[OK] 重写 _file_mode_task")
else:
    print("[FAIL] 找不到 _file_mode_task")

# ── 2. 重写 _write_task_file：生成"给 AI 的任务"格式 ──
OLD_WTF = re.search(r"def _write_task_file\(.*?(?=\n\nclass |\n\ndef |\Z)", text, re.DOTALL)
if OLD_WTF:
    NEW_WTF = '''def _write_task_file(prompt_text, input_text, extra_note, phase_label,
                     chunk_label, out_path, kind="produce"):
    """生成「给 AI 的任务文件」。AI 读这个文件后自己完成任务。"""
    import time as _t
    _TASK_DIR.mkdir(parents=True, exist_ok=True)
    tag = f"{phase_label}__{chunk_label}".replace("/", "_").replace("\\\\", "_")
    safe = "".join(c if c.isalnum() or c in "._-、" else "_" for c in tag)[:80]
    ts = int(_t.time() * 1000) % 1000000
    fp = _TASK_DIR / f"task__{safe}__{ts}.md"

    # 头部：任务说明
    body = f"# 任务：{phase_label}{('（' + chunk_label + '）') if chunk_label else ''}\\n\\n"

    # 你的任务（来自 prompt_text）
    body += "## 你的任务\\n"
    body += (prompt_text or "").strip() + "\\n\\n"

    # 上游资料（只列路径，让 AI 自己读）
    if input_text and str(input_text).strip():
        body += "## 上游资料（读取以下路径的全部内容，作为你的执行依据）\\n"
        body += str(input_text).strip() + "\\n\\n"

    # 输出格式要求
    if extra_note and str(extra_note).strip():
        body += "## 输出格式要求\\n"
        body += str(extra_note).strip() + "\\n\\n"

    # 输出位置
    body += "## 输出位置\\n"
    body += f"把最终结果保存到：{out_path}\\n\\n"

    # 完成判定
    body += "## 完成判定\\n"
    body += f"- 文件 {out_path} 存在\\n"
    body += "- 文件内容非空（≥ 200 字）\\n"
    body += "- 严格按「输出格式要求」执行\\n\\n"

    # 约束
    body += "## 执行约束\\n"
    body += "- 直接用你的文件读取能力读「上游资料」里的路径\\n"
    body += "- 直接用你的文件写入能力写到「输出位置」的路径\\n"
    body += "- 不要输出操作步骤、不要问我确认、不要参考其他内容\\n"
    body += "- 完成后回复「✅ 已完成」\\n"

    fp.write_text(body, encoding="utf-8")
    return fp'''
    text = text[:OLD_WTF.start()] + NEW_WTF + text[OLD_WTF.end():]
    print("[OK] 重写 _write_task_file")
else:
    print("[FAIL] 找不到 _write_task_file")

TARGET.write_text(text, encoding="utf-8")
print(f"\\n[OK] 已写回：{TARGET.name}")
