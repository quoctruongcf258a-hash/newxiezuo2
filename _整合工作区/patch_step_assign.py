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
    """获取/分配步骤号。
    - 同一 task_key（如输出路径）重发 → 返回原步骤号（不 +1）
    - 新 task_key → 分配 = max(现有步骤号) + 1
    """
    import json as _json
    try:
        proj_root = _project_root()
        prog_dir = proj_root / "_progress"
        prog_dir.mkdir(parents=True, exist_ok=True)
        mapping_file = prog_dir / f"{ai_key}_tasks.json"

        mapping = {}
        if mapping_file.exists():
            try:
                mapping = _json.loads(mapping_file.read_text(encoding="utf-8"))
            except Exception:
                mapping = {}

        # 已有 → 复用
        if task_key in mapping:
            return int(mapping[task_key])

        # 新任务 → 分配新号
        max_step = max(mapping.values()) if mapping else 0
        new_step = max_step + 1
        mapping[task_key] = new_step
        mapping_file.write_text(
            _json.dumps(mapping, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return new_step
    except Exception as e:
        print(f"   [step] 分配失败：{e}")
        return 1


def _reset_steps_for_project():
    """清空 _progress/ 目录（新项目开始时调用）。"""
    import shutil as _sh
    try:
        proj_root = _project_root()
        prog_dir = proj_root / "_progress"
        if prog_dir.exists():
            _sh.rmtree(prog_dir)
            print(f"   [step] 已重置 _progress/")
    except Exception:
        pass
'''

anchor = "def _get_ai_steps("
if anchor in text:
    text = text.replace(anchor, FUNC.strip() + "\n\n\n" + anchor, 1)
    print("[OK] 插入 _get_or_assign_step / _reset_steps_for_project")
else:
    print("[FAIL] 找不到 _get_ai_steps 锚点")
    raise SystemExit(1)

TARGET.write_text(text, encoding="utf-8")
print(f"[OK] 已写回 orchestrator.py")
