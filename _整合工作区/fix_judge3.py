import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 完全匹配真实代码（注意最后两行用的是 ai_key 不是 _real）
OLD = '''def _judge_task_status(ai_key, verify_fn, wait_sec):
    """等待 wait_sec，每 5s 检查一次。
    返回 'success' / 'busy' / 'idle_no_output'
    """
    try:
        import sys as _s
        _wu = HERE.parent
        if str(_wu) not in _s.path:
            _s.path.insert(0, str(_wu))
        from mix_send import is_ai_busy
        _real = _resolve_ai_name(ai_key)
    except Exception as _e:
        print(f"   [warn] is_ai_busy 导入失败：{_e}")
        time.sleep(wait_sec)
        ok, _ = verify_fn()
        return "success" if ok else "idle_no_output"

    t0 = time.time()
    while time.time() - t0 < wait_sec:
        if _check_stop():
            return "idle_no_output"
        ok, _ = verify_fn()
        if ok:
            return "success"
        if not is_ai_busy(_real):
            time.sleep(5)
            ok, _ = verify_fn()
            if ok:
                return "success"
            if not is_ai_busy(ai_key):
                return "idle_no_output"
        time.sleep(5)

    return "busy" if is_ai_busy(ai_key) else "idle_no_output"'''

NEW = '''def _judge_task_status(ai_key, verify_fn, wait_sec):
    """等待 wait_sec，每 5s 检查一次。
    返回 'success' / 'busy' / 'idle_no_output'

    关键：发送后 AI 可能还没开始动，必须给足最小反应时间。
    """
    try:
        import sys as _s
        _wu = HERE.parent
        if str(_wu) not in _s.path:
            _s.path.insert(0, str(_wu))
        from mix_send import is_ai_busy
        _real = _resolve_ai_name(ai_key)
    except Exception as _e:
        print(f"   [warn] is_ai_busy 导入失败：{_e}")
        time.sleep(wait_sec)
        ok, _ = verify_fn()
        return "success" if ok else "idle_no_output"

    t0 = time.time()

    # ── 阶段 A：强制等 AI 开始动（最短 30s）──
    MIN_STARTUP = 30
    _check_start_t = time.time()
    while time.time() - _check_start_t < MIN_STARTUP:
        if _check_stop():
            return "idle_no_output"
        ok, _ = verify_fn()
        if ok:
            return "success"
        try:
            if is_ai_busy(_real):
                break
        except Exception:
            pass
        time.sleep(5)

    # ── 阶段 B：正常等待 ──
    _idle_count = 0
    while time.time() - t0 < wait_sec:
        if _check_stop():
            return "idle_no_output"
        ok, _ = verify_fn()
        if ok:
            return "success"
        try:
            _busy = is_ai_busy(_real)
        except Exception:
            _busy = False

        if _busy:
            _idle_count = 0
        else:
            _idle_count += 1
            if _idle_count >= 3:
                print(f"   [{ai_key}] AI 连续 {_idle_count * 5}s 空闲且无产出，判定失败")
                return "idle_no_output"
        time.sleep(5)

    try:
        _busy_end = is_ai_busy(_real)
    except Exception:
        _busy_end = False
    return "busy" if _busy_end else "idle_no_output"'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_judge3")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已替换 _judge_task_status（精确匹配）")
else:
    print("[FAIL] 还是找不到锚点")
    # 打印真实代码的 repr 便于进一步比对
    i = text.find("def _judge_task_status")
    if i >= 0:
        print("\n真实代码 repr（前 1500 字符）：")
        print(repr(text[i:i+1500]))
