import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_wait_ai_task_done" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_unified_wait")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# ── 1. 插入通用等待函数（放在 _check_stop 附近） ──
FUNC = r'''


def _wait_ai_task_done(ai_key, verify_fn, max_wait_sec, min_startup_sec=30):
    """
    通用"等 AI 完成任务"函数——统一忙闲监控逻辑。
    返回 'success' / 'idle_no_output' / 'busy_timeout'

    逻辑：
      阶段A：等 AI 忙起来（最长 min_startup_sec 秒）
             - 如果期间 verify 通过 → success
             - 如果 AI 忙起来 → 进阶段B
             - 如果超时仍不忙 → 进阶段B（给 AI 留反应时间）
      阶段B：等 AI 空闲 + 产出出现（最长 max_wait_sec 秒）
             - verify 通过 → success
             - AI 连续空闲 3 次（15s）+ 无产出 → idle_no_output
             - 超时仍在忙 → busy_timeout
    """
    import time as _t
    import sys as _s
    _wu = HERE.parent
    if str(_wu) not in _s.path:
        _s.path.insert(0, str(_wu))

    try:
        from mix_send import is_ai_busy
        _real = _resolve_ai_name(ai_key)
    except Exception as _e:
        print(f"   [warn] is_ai_busy 导入失败：{_e}")
        _t.sleep(min(max_wait_sec, 60))
        ok, _ = verify_fn()
        return "success" if ok else "idle_no_output"

    # ── 阶段 A：等 AI 开始忙 ──
    _t0 = _t.time()
    while _t.time() - _t0 < min_startup_sec:
        if _check_stop():
            return "idle_no_output"
        ok, _ = verify_fn()
        if ok:
            return "success"
        try:
            if is_ai_busy(_real):
                break   # AI 开始跑了
        except Exception:
            pass
        if not _sleep_breakable(5, 1):
            return "idle_no_output"

    # ── 阶段 B：等 AI 空闲 + 产出 ──
    _t_b = _t.time()
    _idle_count = 0
    while _t.time() - _t_b < max_wait_sec:
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
                print(f"   [{ai_key}] AI 连续 {_idle_count * 5}s 空闲且无产出")
                return "idle_no_output"

        if not _sleep_breakable(5, 1):
            return "idle_no_output"

    # 超时
    try:
        _busy_end = is_ai_busy(_real)
    except Exception:
        _busy_end = False
    return "busy_timeout" if _busy_end else "idle_no_output"
'''

anchor = "def _send_batch_task(ai_key, task_text, dry=False):"
if anchor in text:
    text = text.replace(anchor, FUNC.strip() + "\n\n\n" + anchor, 1)
    print("[OK] 插入 _wait_ai_task_done")

# ── 2. _run_task_stage 用新函数替换 wait_idle 段 ──
OLD1 = '''            if not dry:
                try:
                    import sys as _s
                    _wu = HERE.parent
                    if str(_wu) not in _s.path:
                        _s.path.insert(0, str(_wu))
                    from mix_send import wait_idle
                    _real = _resolve_ai_name(ai_key)
                    if not wait_idle(_real, timeout=30, poll=2):
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception:
                    pass

            print(f"   [{ai_key}] 第 {attempt+1}/{RETRY_MAX_ATTEMPTS} 次（等 {t_wait}s）")
            task_text = task_builder(ai_key)
            if not _send_batch_task(ai_key, task_text, dry):
                ai_attempts["count"] += 1
                ai_attempts["last_error"] = "send_failed"
                continue

            def _vf(_k=ai_key):
                if dry:
                    return True, "dry-run 模拟成功"
                return verify_fn(_k)

            status = _judge_task_status(ai_key, _vf, t_wait) if not dry else "success"'''

NEW1 = '''            print(f"   [{ai_key}] 第 {attempt+1}/{RETRY_MAX_ATTEMPTS} 次（等 {t_wait}s）")

            # 先等 AI 空闲（避免上一个任务的尾巴）
            if not dry:
                try:
                    import sys as _s
                    _wu = HERE.parent
                    if str(_wu) not in _s.path:
                        _s.path.insert(0, str(_wu))
                    from mix_send import wait_idle
                    _real = _resolve_ai_name(ai_key)
                    if not wait_idle(_real, timeout=30, poll=2):
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception:
                    pass

            task_text = task_builder(ai_key)
            if not _send_batch_task(ai_key, task_text, dry):
                ai_attempts["count"] += 1
                ai_attempts["last_error"] = "send_failed"
                continue

            def _vf(_k=ai_key):
                if dry:
                    return True, "dry-run 模拟成功"
                return verify_fn(_k)

            # 用通用等任务函数（内含忙闲监控）
            if dry:
                status = "success"
            else:
                status = _wait_ai_task_done(ai_key, _vf, max_wait_sec=t_wait,
                                             min_startup_sec=30)'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 改 _run_task_stage 用 _wait_ai_task_done")
else:
    print("[WARN] 找不到 _run_task_stage 里的等待段")

# ── 3. _do_produce_batch 用新函数替换 wait_idle 段 ──
OLD2 = '''            if not dry:
                try:
                    import sys as _s
                    _wu = HERE.parent
                    if str(_wu) not in _s.path:
                        _s.path.insert(0, str(_wu))
                    from mix_send import wait_idle
                    _real = _resolve_ai_name(ai_key)
                    if not wait_idle(_real, timeout=30, poll=2):
                        print(f"   [{ai_key}] 等空闲超时")
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception:
                    pass

            print(f"   [{ai_key}] 第 {attempt+1}/{RETRY_MAX_ATTEMPTS} 次（等 {t_wait}s）")
            task_text = build_task(ai_key)
            if not _send_batch_task(ai_key, task_text, dry):
                ai_attempts["count"] += 1
                ai_attempts["last_error"] = "send_failed"
                continue

            # 闭包传入当前 ai_key
            def _vf(_k=ai_key):
                return verify_fn(_k)

            status = _judge_task_status(ai_key, _vf, t_wait) if not dry else "success"'''

NEW2 = '''            print(f"   [{ai_key}] 第 {attempt+1}/{RETRY_MAX_ATTEMPTS} 次（等 {t_wait}s）")

            # 先等 AI 空闲
            if not dry:
                try:
                    import sys as _s
                    _wu = HERE.parent
                    if str(_wu) not in _s.path:
                        _s.path.insert(0, str(_wu))
                    from mix_send import wait_idle
                    _real = _resolve_ai_name(ai_key)
                    if not wait_idle(_real, timeout=30, poll=2):
                        print(f"   [{ai_key}] 等空闲超时")
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception:
                    pass

            task_text = build_task(ai_key)
            if not _send_batch_task(ai_key, task_text, dry):
                ai_attempts["count"] += 1
                ai_attempts["last_error"] = "send_failed"
                continue

            def _vf(_k=ai_key):
                return verify_fn(_k)

            if dry:
                status = "success"
            else:
                status = _wait_ai_task_done(ai_key, _vf, max_wait_sec=t_wait,
                                             min_startup_sec=30)'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 改 _do_produce_batch 用 _wait_ai_task_done")
else:
    print("[WARN] 找不到 _do_produce_batch 里的等待段")

# ── 4. 把 run_task 里的 3 秒校验改成忙闲轮询 ──
OLD3 = '''            if _rs.lstrip().startswith("✅"):
                # 发送后运行校验（3 秒后查「停止」按钮）
                try:
                    time.sleep(3)
                    from mix_send import check_running as _chk
                    _st = _chk(label)
                    if _st == "running":
                        print(f"[校验] ✓ {label} 正在运行")
                    elif _st == "idle":
                        print(f"[校验] ⚠ {label} 未检测到运行（可能已回复完）")
                    else:
                        print(f"[校验] ⚠ {label} 状态：{_st}")
                except Exception as _ve:
                    print(f"[校验] 异常：{_ve}")
                return True'''

NEW3 = '''            if _rs.lstrip().startswith("✅"):
                # 发送后忙闲轮询（20 秒内检测 AI 是否启动）
                try:
                    import sys as _s2
                    _wu2 = HERE.parent
                    if str(_wu2) not in _s2.path:
                        _s2.path.insert(0, str(_wu2))
                    from mix_send import is_ai_busy as _busy_fn
                    _started = False
                    for _i in range(10):
                        time.sleep(2)
                        try:
                            if _busy_fn(label):
                                _started = True
                                print(f"[校验] ✓ {label} 已开始运行（{(_i+1)*2}s 后检测到）")
                                break
                        except Exception:
                            pass
                    if not _started:
                        print(f"[校验] ⚠ {label} 20s 内未检测到运行（可能已秒回或卡住）")
                except Exception as _ve:
                    print(f"[校验] 异常：{_ve}")
                return True'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 改 run_task 的忙闲轮询")
else:
    print("[WARN] 找不到 run_task 校验段")

# 写回
TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 已写回：{TARGET.name}")
