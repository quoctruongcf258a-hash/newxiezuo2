# fix_quest_filemode.py — QUEST 走「读文件」模式（避免输入框卡）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")
changed = []

# 1) 文件头加常量 + 工具函数
if "FILE_MODE_AIS" not in text:
    ANCHOR = 'def _paste_block('
    INSERT = '''# 走「读文件」模式的 AI：这些 AI 的输入框容易卡，改成读文件
FILE_MODE_AIS = {"QUEST"}

# 任务文件目录
import os as _os
_TASK_DIR = Path(r"F:\\赛马23环整合工作室\\程序2改装版\\windows-use\\_scratch\\_task_files")

def _write_task_file(prompt_text, input_text, extra_note, phase_label, chunk_label):
    """把完整指令落到 .md 文件，返回路径。"""
    import time as _t
    _TASK_DIR.mkdir(parents=True, exist_ok=True)
    tag = f"{phase_label}__{chunk_label}".replace("/", "_").replace("\\\\", "_")
    safe = "".join(c if c.isalnum() or c in "._-、" else "_" for c in tag)[:80]
    ts = int(_t.time() * 1000) % 1000000
    fp = _TASK_DIR / f"task__{safe}__{ts}.md"
    body = "===== 指令开始 =====\\n" + (prompt_text or "").strip() + "\\n\\n"
    if input_text and str(input_text).strip():
        body += "【本环节输入材料】\\n" + str(input_text).strip() + "\\n\\n"
    if extra_note and str(extra_note).strip():
        body += "【输出格式要求】\\n" + str(extra_note).strip() + "\\n"
    body += "===== 指令结束 =====\\n"
    fp.write_text(body, encoding="utf-8")
    return fp


def _file_mode_task(app, prompt_text, input_text, extra_note, out_path,
                    phase_label, chunk_label, kind):
    """生成「读文件完成任务」的短指令。kind ∈ {produce, review, merge}"""
    task_file = _write_task_file(prompt_text, input_text, extra_note, phase_label, chunk_label)
    s = _Steps()
    desc = {
        "produce": "完成产出",
        "review": "完成隔离盲审",
        "merge": "完成拼接",
    }.get(kind, "完成任务")
    return f"""任务：用「{app.get('label')}」{desc}（{phase_label}{_chunk_tag(chunk_label)}）。

请读取下面这个文件，按其中的「===== 指令开始 ===== ... ===== 指令结束 =====」之间内容执行：
  {task_file}

完成后，把成品保存到：{out_path}

步骤：
{s()} {_open_instruction(app)}
{s()} {_new_chat_instruction(app)}
{s()} 点击输入框，输入下面这句话并发送（不要粘贴文件内容，只发这句）：
      「请读取文件 {task_file} 的全部内容，按其中【指令开始～指令结束】之间的要求执行，把结果保存到 {out_path}」
{s()} {_wait_instruction()}
{s()} {_save_block(s, out_path, "AI 给出的成品正文")}"""


'''
    if ANCHOR in text:
        text = text.replace(ANCHOR, INSERT + ANCHOR, 1)
        changed.append("插入常量 + 工具函数")

# 2) build_produce_task 加文件模式分支
OLD_P = '''def build_produce_task(app, prompt_text, input_text, out_path, phase_label,
                       chunk_label="", extra_note=""):
    """① 产出：某 AI 在某个「块」上产出一版，落盘到 out_path。

    phase_label 例：'规划 › 主角设计' 或 '写作 › 第0057章 › 分布 › 动'
    chunk_label 例：'能力与能力代价' 或 '六要素·动'
    """
    s = _Steps()'''
NEW_P = '''def build_produce_task(app, prompt_text, input_text, out_path, phase_label,
                       chunk_label="", extra_note=""):
    """① 产出：某 AI 在某个「块」上产出一版，落盘到 out_path。

    phase_label 例：'规划 › 主角设计' 或 '写作 › 第0057章 › 分布 › 动'
    chunk_label 例：'能力与能力代价' 或 '六要素·动'
    """
    if app.get("key") in FILE_MODE_AIS or app.get("prompt_mode") == "file":
        return _file_mode_task(app, prompt_text, input_text, extra_note,
                               out_path, phase_label, chunk_label, "produce")
    s = _Steps()'''
if OLD_P in text:
    text = text.replace(OLD_P, NEW_P, 1)
    changed.append("build_produce_task")
elif "app.get(\"prompt_mode\") == \"file\"" in text:
    print("produce 已改过")

# 3) build_review_task 加文件模式分支
OLD_R = '''    standard_block 为本次要套的审核框架本体：
      规划→八方向该方向的 standards + failPatterns
      写作→六要素该段的 standards + failPatterns + 四条红线
      润色→polishStandard 对应节
      质检→qcStandard 对应节
    """
    s = _Steps()'''
NEW_R = '''    standard_block 为本次要套的审核框架本体：
      规划→八方向该方向的 standards + failPatterns
      写作→六要素该段的 standards + failPatterns + 四条红线
      润色→polishStandard 对应节
      质检→qcStandard 对应节
    """
    if app.get("key") in FILE_MODE_AIS or app.get("prompt_mode") == "file":
        _input_combined = "【本次审核框架】\\n" + (standard_block or "") + "\\n\\n【待审产出】\\n" + (target_text or "")
        return _file_mode_task(app, prompt_text, _input_combined, "",
                               out_path, phase_label, chunk_label, "review")
    s = _Steps()'''
if OLD_R in text:
    text = text.replace(OLD_R, NEW_R, 1)
    changed.append("build_review_task")
elif "review" in text and "prompt_mode" in text:
    print("review 已改过")

# 4) build_merge_task 加文件模式分支
OLD_M = '''    """③ 拼接：指定拼接者读全部版本 + 全部盲审，按段落级择优拼出候选稿。"""
    s = _Steps()'''
NEW_M = '''    """③ 拼接：指定拼接者读全部版本 + 全部盲审，按段落级择优拼出候选稿。"""
    if app.get("key") in FILE_MODE_AIS or app.get("prompt_mode") == "file":
        _input_combined = "【各版本产出】\\n" + (versions_text or "") + "\\n\\n【全部盲审意见】\\n" + (reviews_text or "")
        return _file_mode_task(app, prompt_text, _input_combined, "",
                               out_path, phase_label, chunk_label, "merge")
    s = _Steps()'''
if OLD_M in text:
    text = text.replace(OLD_M, NEW_M, 1)
    changed.append("build_merge_task")
elif "merge" in text and "prompt_mode" in text:
    print("merge 已改过")

if changed:
    bak = TARGET.with_suffix(".py.bak_questfile")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    for c in changed:
        print(f"✔ {c}")
else:
    print("没有改动（或都改过）")