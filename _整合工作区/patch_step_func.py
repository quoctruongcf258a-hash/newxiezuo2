import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_get_or_assign_step" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_step_assign")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

FUNC = r'''


def _get_or_assign_step(ai_key, task_key):
    """按 task_key 分配步骤号：
       - 已有 task_key → 复用原步骤号（重发不 +1）
       - 新 task_key → 分配 = max(现有) + 1
    """
    import json as _json
    try:
        proj_root = _project_root()
        prog_dir = proj_root / "_progress"
        prog_dir.mkdir(parents=True, exist_ok=True)
        mf = prog_dir / f"{ai_key}_tasks.json"

        mapping = {}
        if mf.exists():
            try:
                mapping = _json.loads(mf.read_text(encoding="utf-8"))
            except Exception:
                mapping = {}

        # 已有 → 复用
        if task_key in mapping:
            return int(mapping[task_key])

        # 新任务 → 分配
        max_step = max(mapping.values()) if mapping else 0
        new_step = max_step + 1
        mapping[task_key] = new_step
        mf.write_text(
            _json.dumps(mapping, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return new_step
    except Exception as e:
        print(f"   [step] 分配失败：{e}")
        return 1
'''

anchor = "def _scan_progress("
if anchor in text:
    text = text.replace(anchor, FUNC.strip() + "\n\n\n" + anchor, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已插入 _get_or_assign_step")
else:
    print("[FAIL] 找不到 _scan_progress 锚点")
