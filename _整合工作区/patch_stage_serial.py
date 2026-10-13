import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_stage_serial")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# 找 _run_task_stage 的 ai_order 定义
OLD = '''    ai_order = [primary_ai_key] + list(backup_ai_keys or [])'''
NEW = '''    # 串行/赛马判定：backup_ai_keys 传空 = 赛马（不补），传非空 = 串行（可补）
    ai_order = [primary_ai_key] + list(backup_ai_keys or [])'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] 补丁4：_run_task_stage 加注释")
else:
    print("[WARN] 补丁4 找不到锚点")

# 找 _do_review_batch 里的 backup_keys 构造
OLD2 = '''    all_keys = [p["key"] for p in (sess.get("participants") or [])]
    backup_keys = [k for k in all_keys if k != reviewer_key]

    ok, final_ai = _run_task_stage(
        primary_ai_key=reviewer_key,
        backup_ai_keys=backup_keys,'''

NEW2 = '''    all_keys = [p["key"] for p in (sess.get("participants") or [])]
    _is_serial_r = sess.get("_is_serial_review", True)
    if _is_serial_r:
        backup_keys = [k for k in all_keys if k != reviewer_key]
    else:
        backup_keys = []  # 赛马：失败不补

    ok, final_ai = _run_task_stage(
        primary_ai_key=reviewer_key,
        backup_ai_keys=backup_keys,'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 补丁5：_do_review_batch 串行/赛马分流")
else:
    print("[WARN] 补丁5 找不到锚点")

# _do_merge_batch 同样
OLD3 = '''    all_keys = [p["key"] for p in (sess.get("participants") or [])]
    backup_keys = [k for k in all_keys if k != merger_key]

    ok, final_ai = _run_task_stage(
        primary_ai_key=merger_key,
        backup_ai_keys=backup_keys,'''

NEW3 = '''    all_keys = [p["key"] for p in (sess.get("participants") or [])]
    # 拼接只 1 个 merger → 总是串行（失败换人）
    backup_keys = [k for k in all_keys if k != merger_key]

    ok, final_ai = _run_task_stage(
        primary_ai_key=merger_key,
        backup_ai_keys=backup_keys,'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 补丁6：_do_merge_batch 保持串行")
else:
    print("[WARN] 补丁6 找不到锚点")

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 已写回")
