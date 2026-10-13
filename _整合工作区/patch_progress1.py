import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_scan_progress" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_progress")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# ── 1. 插入 _scan_progress 函数 ──
FUNC = r'''


def _scan_progress(ai_key, expected_items, out_dir, is_single=False):
    """扫 versions/<ai>/ 目录，返回 (已完成数, 总数)。
    is_single：单件模式（生产者），固定文件名
    """
    ai_dir = Path(out_dir) / "versions" / ai_key
    if not ai_dir.exists():
        return 0, len(expected_items)
    done = 0
    for item_key in expected_items:
        if is_single:
            p = ai_dir / f"{item_key}.md"
        else:
            safe = str(item_key).replace("/", "_").replace("\\", "_").replace(":", "_").strip()[:40]
            p = ai_dir / f"{safe}.md"
        if p.exists() and p.stat().st_size >= 200:
            done += 1
    return done, len(expected_items)
'''

anchor = "def _wait_ai_task_done("
if anchor in text:
    text = text.replace(anchor, FUNC.strip() + "\n\n\n" + anchor, 1)
    print("[OK] 插入 _scan_progress")
else:
    print("[FAIL] 找不到锚点")
    raise SystemExit(1)

# ── 2. _wait_ai_task_done 加实时进度打印 ──
OLD = '''    # ── 阶段 A：等 AI 开始忙 ──
    _t0 = _t.time()
    while _t.time() - _t0 < min_startup_sec:'''

NEW = '''    # ── 拿到 expected_items / out_dir / is_single（从闭包传入）──
    _prog_items = locals().get("_progress_items") or []

    # ── 阶段 A：等 AI 开始忙 ──
    _t0 = _t.time()
    _last_prog = -1
    while _t.time() - _t0 < min_startup_sec:'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] 补丁2a：_wait_ai_task_done 阶段A 加进度变量")
else:
    print("[WARN] 找不到阶段A锚点")

# 阶段A 循环里加进度打印
OLD2 = '''        try:
            if is_ai_busy(_real):
                break   # AI 开始跑了
        except Exception:
            pass
        if not _sleep_breakable(5, 1):
            return "idle_no_output"'''

NEW2 = '''        try:
            if is_ai_busy(_real):
                break   # AI 开始跑了
        except Exception:
            pass

        # 实时进度
        if _prog_items:
            _done, _total = _scan_progress(ai_key, _prog_items, out_dir, is_single=_prog_is_single)
            if _done != _last_prog:
                print(f"   [{ai_key}] 📊 进度 {_done}/{_total}")
                _last_prog = _done

        if not _sleep_breakable(5, 1):
            return "idle_no_output"'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 补丁2b：阶段A 加实时进度打印")
else:
    print("[WARN] 找不到阶段A循环锚点")

# 阶段B 循环里也加
OLD3 = '''        if _busy:
            _idle_count = 0
        else:
            _idle_count += 1
            if _idle_count >= 3:
                print(f"   [{ai_key}] AI 连续 {_idle_count * 5}s 空闲且无产出")
                return "idle_no_output"'''

NEW3 = '''        if _busy:
            _idle_count = 0
        else:
            _idle_count += 1
            if _idle_count >= 3:
                print(f"   [{ai_key}] AI 连续 {_idle_count * 5}s 空闲且无产出")
                return "idle_no_output"

        # 实时进度
        if _prog_items:
            _done, _total = _scan_progress(ai_key, _prog_items, out_dir, is_single=_prog_is_single)
            if _done != _last_prog:
                print(f"   [{ai_key}] 📊 进度 {_done}/{_total}")
                _last_prog = _done'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 补丁2c：阶段B 加实时进度打印")
else:
    print("[WARN] 找不到阶段B循环锚点")

# 给 _wait_ai_task_done 加参数
OLD4 = "def _wait_ai_task_done(ai_key, verify_fn, max_wait_sec, min_startup_sec=30):"
NEW4 = "def _wait_ai_task_done(ai_key, verify_fn, max_wait_sec, min_startup_sec=30, _progress_items=None, out_dir=None, _prog_is_single=False):"
if OLD4 in text:
    text = text.replace(OLD4, NEW4, 1)
    print("[OK] 补丁2d：_wait_ai_task_done 加进度参数")
else:
    print("[WARN] 找不到签名")

# 函数体里处理参数
OLD5 = '''    import time as _t
    import sys as _s
    _wu = HERE.parent
    if str(_wu) not in _s.path:
        _s.path.insert(0, str(_wu))'''

NEW5 = '''    import time as _t
    import sys as _s
    _wu = HERE.parent
    if str(_wu) not in _s.path:
        _s.path.insert(0, str(_wu))

    # 进度相关
    _prog_items = _progress_items or []
    _prog_is_single = bool(_prog_is_single)'''

if OLD5 in text:
    text = text.replace(OLD5, NEW5, 1)
    print("[OK] 补丁2e：函数体里初始化进度变量")

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 已写回")
