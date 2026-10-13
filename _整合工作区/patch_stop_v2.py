import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_stopv2")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# ── 1. 新增 _sleep_breakable：替代 time.sleep ──
FUNC = r'''


def _sleep_breakable(sec, step=2):
    """可中断的 sleep：每 step 秒检查一次停止信号。"""
    import time as _t
    _end = _t.time() + sec
    while _t.time() < _end:
        if _check_stop():
            return False
        _t.sleep(min(step, _end - _t.time()))
    return not _check_stop()
'''

if "_sleep_breakable" not in text:
    anchor = "def _send_batch_task(ai_key, task_text, dry=False):"
    text = text.replace(anchor, FUNC.strip() + "\n\n\n" + anchor, 1)
    print("[OK] 插入 _sleep_breakable")

# ── 2. _judge_task_status 里的 time.sleep(5) 改成 _sleep_breakable ──
text = text.replace(
    '''        time.sleep(5)

    # ── 阶段 B：正常等待 ──''',
    '''        if not _sleep_breakable(5, 1):
            return "idle_no_output"

    # ── 阶段 B：正常等待 ──''',
)

text = text.replace(
    '''            _idle_count += 1
            if _idle_count >= 3:
                print(f"   [{ai_key}] AI 连续 {_idle_count * 5}s 空闲且无产出，判定失败")
                return "idle_no_output"
        time.sleep(5)''',
    '''            _idle_count += 1
            if _idle_count >= 3:
                print(f"   [{ai_key}] AI 连续 {_idle_count * 5}s 空闲且无产出，判定失败")
                return "idle_no_output"
        if not _sleep_breakable(5, 1):
            return "idle_no_output"''',
)

# ── 3. _run_task_stage 里的 time.sleep 改 ──
text = text.replace(
    '''                print(f"   [{ai_key}] AI 仍在忙，再等 {RETRY_T_BUSY_LOOP}s")
                time.sleep(RETRY_T_BUSY_LOOP)
                ok, _ = _vf()
                if ok:
                    return True, ai_key''',
    '''                print(f"   [{ai_key}] AI 仍在忙，再等 {RETRY_T_BUSY_LOOP}s")
                if not _sleep_breakable(RETRY_T_BUSY_LOOP, 2):
                    return False, None
                ok, _ = _vf()
                if ok:
                    return True, ai_key''',
)

# ── 4. _do_produce_batch 里的 time.sleep 改 ──
text = text.replace(
    '''                print(f"   [{ai_key}] AI 仍在忙，再等 {RETRY_T_BUSY_LOOP}s")
                time.sleep(RETRY_T_BUSY_LOOP)
                ok, _ = _vf()
                if ok:''',
    '''                print(f"   [{ai_key}] AI 仍在忙，再等 {RETRY_T_BUSY_LOOP}s")
                if not _sleep_breakable(RETRY_T_BUSY_LOOP, 2):
                    return []
                ok, _ = _vf()
                if ok:''',
)

# ── 5. wait_idle 那行改：缩短 timeout，让 _check_stop 频繁有机会跑 ──
text = text.replace(
    '''                    from mix_send import wait_idle
                    _real = _resolve_ai_name(ai_key)
                    if not wait_idle(_real, timeout=300, poll=5):''',
    '''                    from mix_send import wait_idle
                    _real = _resolve_ai_name(ai_key)
                    # 改成 30s 一轮，外层循环每轮查 _check_stop
                    if not wait_idle(_real, timeout=30, poll=2):''',
)

# ── 6. main 里加 KeyboardInterrupt 兜底 ──
OLD_MAIN = '''def main():
    _install_hotkey_listener()
    _clear_stop_signal()
    ap = argparse.ArgumentParser(description="多 AI 协作写作流水线 · 四程序编排")'''

NEW_MAIN = '''def main():
    import signal as _sig

    def _sigint_handler(signum, frame):
        _request_stop("收到 Ctrl+C")
        # 第二次 Ctrl+C 直接退出
        import signal as _s2
        _s2.signal(_s2.SIGINT, _s2.SIG_DFL)

    try:
        _sig.signal(_sig.SIGINT, _sigint_handler)
    except Exception:
        pass

    _install_hotkey_listener()
    _clear_stop_signal()
    ap = argparse.ArgumentParser(description="多 AI 协作写作流水线 · 四程序编排")'''

if OLD_MAIN in text:
    text = text.replace(OLD_MAIN, NEW_MAIN, 1)
    print("[OK] main 加 Ctrl+C 处理")

# 写回
TARGET.write_text(text, encoding="utf-8")
print("[OK] 已写回")
