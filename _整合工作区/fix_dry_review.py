import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

changed = 0

# ── 修 1：_do_review_batch 里 dry 时跳过目录检查 ──
OLD1 = '''    versions_dir = Path(out_dir) / "versions"
    if not versions_dir.exists():
        return None
    all_ai_dirs = [d for d in versions_dir.iterdir() if d.is_dir()]
    read_dirs = [d for d in all_ai_dirs if d.name != reviewer_key]

    if not read_dirs:
        print(f"   [{reviewer_key}] 没有其他 AI 的产出可审，跳过")
        return None'''

NEW1 = '''    versions_dir = Path(out_dir) / "versions"
    if dry:
        # dry-run 不写文件，伪造 read_dirs 让流程继续
        read_dirs = [versions_dir / k for k in
                     [p["key"] for p in (sess.get("participants") or [])]
                     if k != reviewer_key]
    else:
        if not versions_dir.exists():
            return None
        all_ai_dirs = [d for d in versions_dir.iterdir() if d.is_dir()]
        read_dirs = [d for d in all_ai_dirs if d.name != reviewer_key]

    if not read_dirs:
        print(f"   [{reviewer_key}] 没有其他 AI 的产出可审，跳过")
        return None'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 修1：_do_review_batch dry 兼容")
    changed += 1
else:
    print("[FAIL] 修1 找不到锚点")

# ── 修 2：_run_task_stage 里 dry 时 verify_fn 直接返回成功 ──
OLD2 = '''            def _vf(_k=ai_key):
                return verify_fn(_k)

            status = _judge_task_status(ai_key, _vf, t_wait) if not dry else "success"'''

NEW2 = '''            def _vf(_k=ai_key):
                if dry:
                    return True, "dry-run 模拟成功"
                return verify_fn(_k)

            status = _judge_task_status(ai_key, _vf, t_wait) if not dry else "success"'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 修2：_run_task_stage dry 兼容")
    changed += 1
else:
    print("[FAIL] 修2 找不到锚点")

# 写回
if changed >= 1:
    bak = TARGET.with_suffix(".py.bak_dry_review")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回（{changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处")
