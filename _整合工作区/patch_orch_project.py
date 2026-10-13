# patch_orch_project.py — orchestrator 读当前项目名 + 输出到 output/<项目>/
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")


def main():
    print("=" * 60)
    print("patch_orch_project")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_PROJECT_ROOT" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_projroot")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # ── 改动 1：顶部加 _load_project / _project_root ──
    anchor = "RINGS_JSON = HERE.parent.parent / \"rules\" / \"rings_items.json\"\n"
    if anchor not in text:
        print("[失败] 找不到 RINGS_JSON 锚点")
        return
    insert = anchor + '''

# _PROJECT_ROOT：读当前项目名，算产物根目录
PROJECT_FILE = HERE.parent / "work" / "collab" / "current_project.json"
OUTPUT_DIR = HERE.parent.parent / "output"


def _load_current_project():
    """从 work/collab/current_project.json 读项目名。"""
    if PROJECT_FILE.exists():
        try:
            import json as _json
            _d = _json.loads(PROJECT_FILE.read_text(encoding="utf-8"))
            _p = _d.get("project") or ""
            if _p:
                return _p
        except Exception:
            pass
    return ""


def _project_root():
    """返回 output/<项目名>/；无项目名时回退 windows-use/work/。"""
    _p = _load_current_project()
    if _p:
        return OUTPUT_DIR / _p
    return HERE.parent / "work"


# 阶段名映射：程序名 → output 下的子目录
_STAGE_DIR_MAP = {
    "规划": "01_规划",
    "写作": "02_写作",
    "润色": "03_去AI",
    "质检": "04_审核",
}
'''
    text = text.replace(anchor, insert, 1)
    print("✔ 改动1：加了 _load_current_project / _project_root")

    # ── 改动 2：phase_dir 改用 _project_root ──
    old_dir = '''def phase_dir(program, chapter, phase_key):
    d = WORK / program
    if chapter:
        d = d / f"ch{chapter}"
    return d / phase_key
'''
    new_dir = '''def phase_dir(program, chapter, phase_key):
    """_PROJECT_ROOT：产物写到 output/<项目名>/<阶段目录>/<环名>/"""
    _stage = _STAGE_DIR_MAP.get(program, program)
    d = _project_root() / _stage
    if chapter:
        d = d / f"ch{chapter}"
    return d / phase_key
'''
    if old_dir not in text:
        print("[失败] 找不到 phase_dir 函数")
        return
    text = text.replace(old_dir, new_dir, 1)
    print("✔ 改动2：phase_dir 改用 output/<项目>/<阶段>/<环>/")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()