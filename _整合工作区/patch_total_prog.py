import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_scan_total_progress" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_total_prog")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# ── 插入 _scan_total_progress ──
FUNC = r'''


def _scan_total_progress(ai_key, out_dir):
    """扫该 AI 在当前环节的累计进度：
       - versions/<ai>/*.md  （产出）
       - reviews/<ai>/*.json （盲审）
    返回 (已完成, 总任务数)
    """
    versions_dir = Path(out_dir) / "versions" / ai_key
    reviews_dir = Path(out_dir) / "reviews" / ai_key

    prod_done = 0
    if versions_dir.exists():
        for f in versions_dir.glob("*.md"):
            if f.exists() and f.stat().st_size >= 200:
                prod_done += 1

    rev_done = 0
    if reviews_dir.exists():
        for f in reviews_dir.glob("*.json"):
            if f.exists() and f.stat().st_size >= 100:
                rev_done += 1

    # 总任务数 = 产出数 + 盲审数（不是固定，动态统计）
    # 如果还没开始，用 target = prod_done 或 rev_done 之一
    total = max(prod_done + rev_done, 1)
    return prod_done + rev_done, total
'''

anchor = "def _wait_ai_task_done("
if anchor in text:
    text = text.replace(anchor, FUNC.strip() + "\n\n\n" + anchor, 1)
    print("[OK] 插入 _scan_total_progress")
else:
    print("[FAIL] 找不到锚点")
    raise SystemExit(1)

# ── 改 _wait_ai_task_done 里的进度打印 ──
OLD = '''        # 实时进度
        if _prog_items:
            _done, _total = _scan_progress(ai_key, _prog_items, out_dir, is_single=_prog_is_single)
            if _done != _last_prog:
                print(f"   [{ai_key}] 📊 进度 {_done}/{_total}")
                _last_prog = _done'''

NEW = '''        # 实时累计进度（含产出 + 盲审）
        if out_dir is not None:
            _done, _total = _scan_total_progress(ai_key, out_dir)
            # 加上"本环节预期总任务数"（从调用方传）
            _expect_total = _prog_total or _total
            if _done != _last_prog:
                print(f"   [{ai_key}] 📊 进度 {_done}/{_expect_total}")
                _last_prog = _done'''

cnt = text.count(OLD)
if cnt > 0:
    text = text.replace(OLD, NEW)
    print(f"[OK] 改 _wait_ai_task_done 的进度打印（{cnt} 处）")
else:
    print("[WARN] 找不到进度打印锚点")

# ── 给 _wait_ai_task_done 加 _prog_total 参数 ──
OLD2 = "def _wait_ai_task_done(ai_key, verify_fn, max_wait_sec, min_startup_sec=30, _progress_items=None, out_dir=None, _prog_is_single=False):"
NEW2 = "def _wait_ai_task_done(ai_key, verify_fn, max_wait_sec, min_startup_sec=30, _progress_items=None, out_dir=None, _prog_is_single=False, _prog_total=None):"
if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] _wait_ai_task_done 加 _prog_total")
else:
    print("[WARN] 找不到签名")

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 已写回")
