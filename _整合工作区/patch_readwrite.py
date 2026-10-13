# patch_readwrite.py — 提示词里注入「读取资料路径」+「完成判定」
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")


def main():
    print("=" * 60)
    print("patch_readwrite")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_UPSTREAM_PATHS" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_rw")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # ── 1. 加 _upstream_files 辅助函数，插在 phase_dir 之前 ──
    anchor = "def phase_dir(program, chapter, phase_key):\n"
    if anchor not in text:
        print("[失败] 找不到 phase_dir 锚点")
        return
    helper = '''# _UPSTREAM_PATHS：列出本环之前已产出的文件路径
def _upstream_files(program, phase_cfg, chapter=None):
    """返回本环应读取的上游文件路径列表。"""
    _root = _project_root()
    _stage = _STAGE_DIR_MAP.get(program, program)
    _stage_dir = _root / _stage
    ups = []

    # 首个程序（规划）读 00_初始化 的项目信息
    if program == "规划":
        _info = _root / "00_初始化" / "项目信息.json"
        if _info.exists():
            ups.append(str(_info))

    # 读前面环的 phase_candidate.md（按 rings_items.json 顺序）
    try:
        import json as _json
        if RINGS_JSON.exists():
            _rings = _json.loads(RINGS_JSON.read_text(encoding="utf-8"))
            _stage_key = {"规划": "01_规划", "写作": "02_写作",
                          "润色": "03_去AI", "质检": "04_审核"}.get(program, "")
            _items = _rings.get(_stage_key, {}).get("环节", [])
            _order = [x.get("name") or x.get("code") for x in _items]
            _cur = phase_cfg.get("key") or phase_cfg.get("name")
            if _cur in _order:
                _idx = _order.index(_cur)
                for _prev in _order[:_idx]:
                    fp = _stage_dir / _prev / "phase_candidate.md"
                    if fp.exists():
                        ups.append(str(fp))
    except Exception:
        pass

    # 章循环：读上一章产物
    if chapter and program in ("写作", "润色", "质检"):
        try:
            _prev_ch = str(int(chapter) - 1).zfill(4)
            _prev_dir = _root / "02_写作" / f"ch{_prev_ch}"
            if _prev_dir.exists():
                for _fp in _prev_dir.rglob("phase_candidate.md"):
                    ups.append(str(_fp))
        except Exception:
            pass

    return ups


def phase_dir(program, chapter, phase_key):
'''
    text = text.replace(anchor, helper, 1)
    print("✔ 改动1：加了 _upstream_files 函数")

    # ── 2. phase_input 里注入「读取资料路径」+「完成判定」──
    inject_anchor = '    parts = []\n\n    # _INJECT_DESC：'
    if inject_anchor not in text:
        print("[失败] 找不到 phase_input 里 _INJECT_DESC 锚点")
        return

    new_inject = '''    parts = []

    # _UPSTREAM_PATHS：注入读取路径 + 完成判定
    _ups = _upstream_files(program, phase_cfg, chapter)
    _out_dir = phase_dir(program, chapter, phase_cfg["key"])
    _read_block = "【读取资料（逐字读，唯一依据）】"
    if _ups:
        for _f in _ups:
            _read_block += f"\\n  · {_f}"
    else:
        _read_block += "\\n  （本环是第一个环节，无上游产物）"
    _read_block += (
        "\\n\\n【本环节输出路径（写到这里才算完成）】"
        f"\\n  {_out_dir / 'versions' / (phase_cfg['key'] + '__<你的名字>.md')}"
        "\\n\\n【完成判定】"
        "\\n  任务完成 = 下列全部满足："
        "\\n    1. 文件已保存到上面「输出路径」"
        "\\n    2. 文件内容非空（≥200 字）"
        "\\n    3. 严格按【输出格式要求】执行"
        "\\n    4. 只输出本块成品，不越界"
    )
    parts.append(_read_block)

    # _INJECT_DESC：'''
    text = text.replace(inject_anchor, new_inject, 1)
    print("✔ 改动2：phase_input 里注入「读取路径 + 输出路径 + 完成判定」")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()