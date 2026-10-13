import shutil
from pathlib import Path

T1 = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text1 = T1.read_text(encoding="utf-8")

bak1 = T1.with_suffix(".py.bak_ai_key")
if not bak1.exists():
    shutil.copy(T1, bak1)
    print(f"已备份：{bak1.name}")

# 改函数签名
OLD_SIG = "def _write_task_file(prompt_text, input_text, extra_note, phase_label,\n                     chunk_label, out_path, kind=\"produce\"):"
NEW_SIG = "def _write_task_file(prompt_text, input_text, extra_note, phase_label,\n                     chunk_label, out_path, kind=\"produce\", ai_key=\"unknown\"):"

if OLD_SIG in text1:
    text1 = text1.replace(OLD_SIG, NEW_SIG, 1)
    print("[OK] 修1a：_write_task_file 加 ai_key 参数")
else:
    print("[FAIL] 修1a 找不到锚点")

# 改文件名生成
OLD_NAME = '    ts = int(_t.time() * 1000) % 1000000\n    fp = _TASK_DIR / f"task__{safe}__{ts}.md"'
NEW_NAME = '''    ts = int(_t.time() * 1000) % 1000000
    _safe_ai = "".join(c if c.isalnum() or c in "._-" else "_" for c in ai_key)[:20]
    fp = _TASK_DIR / f"task__{safe}__{_safe_ai}__{ts}.md"'''

if OLD_NAME in text1:
    text1 = text1.replace(OLD_NAME, NEW_NAME, 1)
    print("[OK] 修1b：文件名加 ai_key")
else:
    print("[FAIL] 修1b 找不到锚点")

# 改调用处
OLD_CALL = "    task_file = _write_task_file(prompt_text, input_text, extra_note,\n                                  phase_label, chunk_label, out_path, kind)"
NEW_CALL = '    _ai = app.get("key") or "unknown"\n    task_file = _write_task_file(prompt_text, input_text, extra_note,\n                                  phase_label, chunk_label, out_path, kind,\n                                  ai_key=_ai)'

if OLD_CALL in text1:
    text1 = text1.replace(OLD_CALL, NEW_CALL, 1)
    print("[OK] 修1c：_file_mode_task 传 ai_key")
else:
    print("[FAIL] 修1c 找不到锚点")

# 任务文件头部加身份
OLD_BODY = '''    # 头部：任务说明
    body = f"# 任务：{phase_label}{('（' + chunk_label + '）') if chunk_label else ''}\\n\\n"'''
NEW_BODY = '''    # 头部：任务说明 + AI 身份声明
    body = f"# 任务：{phase_label}{('（' + chunk_label + '）') if chunk_label else ''}\\n\\n"
    body += f"> 执行者：{ai_key}\\n\\n"'''

if OLD_BODY in text1:
    text1 = text1.replace(OLD_BODY, NEW_BODY, 1)
    print("[OK] 修1d：任务文件头部加 AI 身份")
else:
    print("[FAIL] 修1d 找不到锚点")

T1.write_text(text1, encoding="utf-8")
print(f"\n[OK] 已写回：{T1.name}")
