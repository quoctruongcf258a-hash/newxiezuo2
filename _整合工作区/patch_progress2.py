import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# _do_produce_batch 里调用 _wait_ai_task_done 时传参
OLD = '''            if dry:
                status = "success"
            else:
                status = _wait_ai_task_done(ai_key, _vf, max_wait_sec=t_wait,
                                             min_startup_sec=30)'''

NEW = '''            if dry:
                status = "success"
            else:
                _prog_items = [k for k, _ in expected]
                status = _wait_ai_task_done(
                    ai_key, _vf, max_wait_sec=t_wait, min_startup_sec=30,
                    _progress_items=_prog_items,
                    out_dir=out_dir,
                    _prog_is_single=_is_single,
                )'''

cnt = text.count(OLD)
if cnt > 0:
    text = text.replace(OLD, NEW)
    bak = TARGET.with_suffix(".py.bak_progress2")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"[OK] _do_produce_batch 调用点加进度参数（{cnt} 处）")
else:
    print("[FAIL] 找不到调用点")
    i = text.find("_wait_ai_task_done(ai_key, _vf")
    if i >= 0:
        print(f"\n附近代码：")
        print(text[i-100:i+300])
