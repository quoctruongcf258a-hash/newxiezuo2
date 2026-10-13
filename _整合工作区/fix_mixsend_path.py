import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 修复 _send_batch_task 里的 mix_send 导入
OLD = '''def _send_batch_task(ai_key, task_text, dry=False):
    """发送任务到指定 AI。返回 True/False。"""
    if dry:
        return True
    try:
        from mix_send import send
        r = send(ai_key, task_text)
        rs = str(r or "").lstrip()
        if rs.startswith("✅"):
            print(f"   [{ai_key}] 任务已发送")
            return True
        print(f"   [{ai_key}] 发送返回异常：{rs[:80]}")
        return False
    except Exception as e:
        print(f"   [{ai_key}] 发送失败：{e}")
        return False'''

NEW = '''def _send_batch_task(ai_key, task_text, dry=False):
    """发送任务到指定 AI。返回 True/False。"""
    if dry:
        return True
    try:
        import sys as _s
        _wu = HERE.parent
        if str(_wu) not in _s.path:
            _s.path.insert(0, str(_wu))
        from mix_send import send
        r = send(ai_key, task_text)
        rs = str(r or "").lstrip()
        if rs.startswith("✅"):
            print(f"   [{ai_key}] 任务已发送")
            return True
        print(f"   [{ai_key}] 发送返回异常：{rs[:80]}")
        return False
    except Exception as e:
        print(f"   [{ai_key}] 发送失败：{e}")
        return False'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] 修复：_send_batch_task 加 sys.path 处理")
else:
    print("[FAIL] 找不到锚点")

# 顺便检查 _judge_task_status 里的 mix_send 导入
OLD2 = '''    try:
        from mix_send import is_ai_busy
    except Exception:
        time.sleep(wait_sec)
        ok, _ = verify_fn()
        return "success" if ok else "idle_no_output"'''

NEW2 = '''    try:
        import sys as _s
        _wu = HERE.parent
        if str(_wu) not in _s.path:
            _s.path.insert(0, str(_wu))
        from mix_send import is_ai_busy
    except Exception as _e:
        print(f"   [warn] is_ai_busy 导入失败：{_e}")
        time.sleep(wait_sec)
        ok, _ = verify_fn()
        return "success" if ok else "idle_no_output"'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 修复：_judge_task_status 加 sys.path 处理")
else:
    print("[INFO] _judge_task_status 里已经是完整的，或锚点不同")

# 检查 _run_task_stage 里的 wait_idle 导入
OLD3 = '''            if not dry:
                try:
                    from mix_send import wait_idle
                    if not wait_idle(ai_key, timeout=300, poll=5):
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception:
                    pass'''

NEW3 = '''            if not dry:
                try:
                    import sys as _s
                    _wu = HERE.parent
                    if str(_wu) not in _s.path:
                        _s.path.insert(0, str(_wu))
                    from mix_send import wait_idle
                    if not wait_idle(ai_key, timeout=300, poll=5):
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception:
                    pass'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 修复：_run_task_stage 加 sys.path 处理")

# _do_produce_batch 里也有 wait_idle
OLD4 = '''            if not dry:
                try:
                    from mix_send import wait_idle
                    if not wait_idle(ai_key, timeout=300, poll=5):
                        print(f"   [{ai_key}] 等空闲超时")
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception:
                    pass'''

NEW4 = '''            if not dry:
                try:
                    import sys as _s
                    _wu = HERE.parent
                    if str(_wu) not in _s.path:
                        _s.path.insert(0, str(_wu))
                    from mix_send import wait_idle
                    if not wait_idle(ai_key, timeout=300, poll=5):
                        print(f"   [{ai_key}] 等空闲超时")
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception:
                    pass'''

if OLD4 in text:
    text = text.replace(OLD4, NEW4, 1)
    print("[OK] 修复：_do_produce_batch 加 sys.path 处理")

# 写回
bak = TARGET.with_suffix(".py.bak_mixsend_path")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")
TARGET.write_text(text, encoding="utf-8")
print("[OK] 已写回")
