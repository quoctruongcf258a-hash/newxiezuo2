import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_step_assign2")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# 替换 _get_current_step
OLD = '''# 动态步骤号：从 orchestrator 的 _get_ai_steps 读
def _get_current_step(ai_key):
    """读该 AI 的当前步骤号（已完成 + 1 = 即将执行的步骤）。"""
    try:
        from orchestrator import _get_ai_steps
        return _get_ai_steps(ai_key) + 1
    except Exception:
        return 1'''

NEW = '''# 动态步骤号：按任务标识分配（重发复用，新任务 +1）
def _get_current_step(ai_key, task_key):
    """按 task_key 获取/分配步骤号。"""
    try:
        from orchestrator import _get_or_assign_step
        return _get_or_assign_step(ai_key, task_key)
    except Exception as e:
        print(f"   [step] 获取失败：{e}")
        return 1'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] tasks.py 换成 _get_or_assign_step")
else:
    print("[WARN] 找不到 _get_current_step")

# 改调用点：_file_mode_task 里传 out_path 作为 task_key
OLD2 = '    _step_no = _get_current_step(app.get("key") or "unknown")'
NEW2 = '''    # 用 out_path 作为任务唯一标识
    _task_key = str(out_path).replace("\\\\", "/")
    _step_no = _get_current_step(app.get("key") or "unknown", _task_key)'''

cnt = text.count(OLD2)
if cnt > 0:
    text = text.replace(OLD2, NEW2)
    print(f"[OK] _file_mode_task 传 task_key（{cnt} 处）")
else:
    print("[WARN] 找不到 _step_no 调用点")

TARGET.write_text(text, encoding="utf-8")
print(f"[OK] 已写回 tasks.py")
