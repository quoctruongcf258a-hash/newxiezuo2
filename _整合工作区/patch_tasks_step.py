import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_step_total")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

changed = 0

# ── 1. _file_mode_task 加 total_steps / stage_start / stage_end 参数 ──
OLD1 = '''def _file_mode_task(app, prompt_text, input_text, extra_note, out_path,
                    phase_label, chunk_label, kind):'''
NEW1 = '''def _file_mode_task(app, prompt_text, input_text, extra_note, out_path,
                    phase_label, chunk_label, kind,
                    total_steps=None, stage_end=None):'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 改1：_file_mode_task 加参数")
    changed += 1
else:
    print("[FAIL] 改1 找不到锚点")

# ── 2. 改外层 prompt 的"回复模板" ──
OLD2 = '''    _ai = app.get("key") or "unknown"
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

NEW2 = '''    _ai = app.get("key") or "unknown"
    # 步骤显示：如果给了 total_steps / stage_end，显示"当前步数/总步数"
    if total_steps and stage_end:
        _step_marker = f"{stage_end}/{total_steps}"
    else:
        _step_marker = "<已完成数>/<总文件数>"

    return (
        f"请读取文件：{task_file}\\n"
        f"按文件里「## 你的任务」章节的要求执行。\\n"
        f"完成后，按文件里「## 输出位置」章节的路径保存结果。\\n"
        f"最后**必须**回复这一行（一字不改）：\\n"
        f"  ✅ [{_ai}] {phase_label} → {_step_marker} 已完成\\n"
        f"  生成文件列表：\\n"
        f"    - <文件名1>\\n"
        f"    - <文件名2>\\n"
        f"    - ...\\n"
        f"不要输出多余说明。"
    )'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 改2：外层 prompt 用 stage_end/total_steps")
    changed += 1
else:
    print("[FAIL] 改2 找不到外层 prompt 锚点")

# ── 3. 改任务文件里的"回复模板" ──
OLD3 = '''    # 回复标识：带 ai_key + 环节名 + 文件进度
    body += f"- 完成后，**必须**回复这一行（一字不改，注意带文件清单）：\\n"
    body += f"  `✅ [{ai_key}] {phase_label} → <已完成数>/<总文件数> 已完成`\\n"
    body += f"  生成文件列表：\\n"
    body += f"    - <文件名1>\\n"
    body += f"    - <文件名2>\\n"
    body += f"    - ...\\n"
    body += f"- 如果失败，回复 `❌ [{ai_key}] {phase_label} 失败：<原因>`\\n"'''

NEW3 = '''    # 回复标识：带 ai_key + 环节名 + 步骤进度
    if total_steps and stage_end:
        _step_marker = f"{stage_end}/{total_steps}"
    else:
        _step_marker = "<已完成数>/<总文件数>"

    body += f"- 完成后，**必须**回复这一行（一字不改）：\\n"
    body += f"  `✅ [{ai_key}] {phase_label} → {_step_marker} 已完成`\\n"
    body += f"  生成文件列表：\\n"
    body += f"    - <文件名1>\\n"
    body += f"    - <文件名2>\\n"
    body += f"    - ...\\n"
    body += f"- 如果失败，回复 `❌ [{ai_key}] {phase_label} 失败：<原因>`\\n"'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 改3：任务文件回复用 stage_end/total_steps")
    changed += 1
else:
    print("[FAIL] 改3 找不到任务文件回复锚点")

# ── 4. _write_task_file 加 total_steps / stage_end 参数 ──
OLD4 = '''def _write_task_file(prompt_text, input_text, extra_note, phase_label,
                     chunk_label, out_path, kind="produce", ai_key="unknown"):'''
NEW4 = '''def _write_task_file(prompt_text, input_text, extra_note, phase_label,
                     chunk_label, out_path, kind="produce", ai_key="unknown",
                     total_steps=None, stage_end=None):'''

if OLD4 in text:
    text = text.replace(OLD4, NEW4, 1)
    print("[OK] 改4：_write_task_file 加参数")
    changed += 1
else:
    print("[FAIL] 改4 找不到签名")

# ── 5. _file_mode_task 里调用 _write_task_file 时传参 ──
OLD5 = '''    _ai = app.get("key") or "unknown"
    task_file = _write_task_file(prompt_text, input_text, extra_note,
                                  phase_label, chunk_label, out_path, kind,
                                  ai_key=_ai)'''
NEW5 = '''    _ai = app.get("key") or "unknown"
    task_file = _write_task_file(prompt_text, input_text, extra_note,
                                  phase_label, chunk_label, out_path, kind,
                                  ai_key=_ai,
                                  total_steps=total_steps, stage_end=stage_end)'''

if OLD5 in text:
    text = text.replace(OLD5, NEW5, 1)
    print("[OK] 改5：传递 total_steps/stage_end")
    changed += 1
else:
    print("[FAIL] 改5 找不到调用锚点")

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 共修改 {changed} 处")
