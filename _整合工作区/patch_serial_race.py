import shutil
from pathlib import Path
import re

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_serial_mode")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

changed = 0

# ── 1. _run_batch_mesh 里判定串行/赛马，写入 sess ──
OLD1 = '''def _run_batch_mesh(
    agent, sess, cfg, program, phase_cfg, chapter,
    input_text, out_dir, dry,
    writers, reviewers, merger, split_spec,
):
    """批量模式下跑整个环节：产出 → 盲审 → 拼接（多AI）/ 修改（单AI）。"""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    versions_dir = Path(out_dir) / "versions"'''

NEW1 = '''def _run_batch_mesh(
    agent, sess, cfg, program, phase_cfg, chapter,
    input_text, out_dir, dry,
    writers, reviewers, merger, split_spec,
):
    """批量模式下跑整个环节：产出 → 盲审 → 拼接（多AI）/ 修改（单AI）。

    串行/赛马判定：
      - 产出 AI 数 = 1 → 串行（失败换人）
      - 产出 AI 数 >= 2 → 赛马（失败淘汰，不补）
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # ── 判断串行/赛马 ──
    is_serial_produce = (len(writers) == 1)
    is_serial_review = (len(reviewers) <= 1)
    sess["_is_serial_produce"] = is_serial_produce
    sess["_is_serial_review"] = is_serial_review

    _mode_str = "串行（失败换人）" if is_serial_produce else f"赛马（{len(writers)} AI 竞争）"
    print(f"   [模式] 产出：{_mode_str}")
    if reviewers:
        _r_str = "串行（失败换人）" if is_serial_review else f"赛马（{len(reviewers)} AI 盲审）"
        print(f"   [模式] 盲审：{_r_str}")

    versions_dir = Path(out_dir) / "versions"'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 补丁1：_run_batch_mesh 判定串行/赛马")
    changed += 1
else:
    print("[FAIL] 补丁1 找不到锚点")

# ── 2. _do_produce_batch 读 sess 标记 ──
OLD2 = '''    _all_parts = sess.get("participants") or []
    primary_key = app["key"]
    backup_keys = [p["key"] for p in _all_parts if p["key"] != primary_key]'''

NEW2 = '''    _all_parts = sess.get("participants") or []
    primary_key = app["key"]

    # ── 串行/赛马判定 ──
    _is_serial = sess.get("_is_serial_produce", True)
    if _is_serial:
        # 串行：其他所有在线 AI 都可以替换
        backup_keys = [p["key"] for p in _all_parts if p["key"] != primary_key]
        print(f"   [串行] 主 AI = {primary_key}，备用 = {backup_keys}")
    else:
        # 赛马：无备用，失败即淘汰
        backup_keys = []
        print(f"   [赛马] AI = {primary_key}，失败将被淘汰（无替补）")'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 补丁2：_do_produce_batch 读串行/赛马标记")
    changed += 1
else:
    print("[WARN] 补丁2 找不到锚点（可能在别的函数里）")

# ── 3. _do_produce_batch 全失败时，不写 _failed（赛马模式只淘汰）──
OLD3 = '''    # 全部失败
    _write_failed_record(project_root, phase_key, "产出",
                          attempts_log, build_task(primary_key)[:300])
    print(f"\\n   ⛔ [{phase_key}] 产出阶段全 AI 失败，已写 _failed/")
    return []'''

NEW3 = '''    # 全部失败
    if _is_serial:
        # 串行：写 _failed 记录（等人工介入）
        _write_failed_record(project_root, phase_key, "产出",
                              attempts_log, build_task(primary_key)[:300])
        print(f"\\n   ⛔ [{phase_key}] 串行产出失败（所有 AI 都试过）")
        print(f"   ⛔ 已写 _failed/，需人工介入")
    else:
        # 赛马：该 AI 淘汰，不写 _failed（其他 AI 的产出仍有效）
        print(f"\\n   ⚠️ [{primary_key}] 赛马模式 3 次失败，本轮退出")
        print(f"   （其他 AI 不受影响，继续完成）")
    return []'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 补丁3：全失败时串行/赛马分流")
    changed += 1
else:
    print("[WARN] 补丁3 找不到锚点")

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 共修改 {changed} 处")
