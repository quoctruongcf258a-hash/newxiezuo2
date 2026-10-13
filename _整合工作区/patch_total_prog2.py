import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 找 _run_batch_mesh 里调用 do_produce 的地方，加 _prog_total
# 但 _prog_total 会传到 _do_produce_batch → _wait_ai_task_done

# 简化为：在 _do_produce_batch 里直接算 _prog_total
OLD = '''    _is_single = (len(expected) == 1)'''

NEW = '''    _is_single = (len(expected) == 1)
    # 本环节该 AI 的总任务数 = 产出数 × 2（产出 + 盲审）
    _prog_total = len(expected) * 2'''

cnt = text.count(OLD)
if cnt > 0:
    text = text.replace(OLD, NEW, 1)
    print(f"[OK] _do_produce_batch 加 _prog_total 计算")

# 调用 _wait_ai_task_done 时传 _prog_total
OLD2 = '''                _prog_items = [k for k, _ in expected]
                status = _wait_ai_task_done(
                    ai_key, _vf, max_wait_sec=t_wait, min_startup_sec=30,
                    _progress_items=_prog_items,
                    out_dir=out_dir,
                    _prog_is_single=_is_single,
                )'''

NEW2 = '''                _prog_items = [k for k, _ in expected]
                status = _wait_ai_task_done(
                    ai_key, _vf, max_wait_sec=t_wait, min_startup_sec=30,
                    _progress_items=_prog_items,
                    out_dir=out_dir,
                    _prog_is_single=_is_single,
                    _prog_total=_prog_total,
                )'''

cnt = text.count(OLD2)
if cnt > 0:
    text = text.replace(OLD2, NEW2)
    bak = TARGET.with_suffix(".py.bak_total_prog2")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"[OK] 传 _prog_total（{cnt} 处）")
else:
    print("[WARN] 找不到 _wait_ai_task_done 调用锚点")
