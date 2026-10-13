# patch_orch_roles.py — orchestrator 按 UI 的 stage_board.json 派角色
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")


def main():
    print("=" * 60)
    print("patch_orch_roles")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_roles_from_stage_board" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_roles")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # ── 改动 1：在 RINGS_JSON 后插入 3 个辅助函数 ──
    a1 = 'RINGS_JSON = HERE.parent.parent / "rules" / "rings_items.json"\n'
    if a1 not in text:
        print("[失败] 找不到 RINGS_JSON 锚点")
        return
    b1 = a1 + '''

# _roles_from_stage_board：读 UI 的 stage_board.json 拿角色指派
STAGE_BOARD_PATHS = [
    HERE.parent.parent / "work" / "collab" / "stage_board.json",
    HERE.parent / "work" / "collab" / "stage_board.json",
]


def load_stage_assignments():
    for _p in STAGE_BOARD_PATHS:
        if _p.exists():
            try:
                _d = json.loads(_p.read_text(encoding="utf-8"))
                return _d.get("assignments", {}) or {}
            except Exception:
                pass
    return {}


def _name_to_key(name, participants):
    if not name:
        return None
    for _p in participants:
        if _p.get("label") == name or _p.get("key") == name:
            return _p["key"]
    return (name or "").lower().replace(" ", "_")


def _names_to_parts(names, participants):
    if isinstance(names, str):
        names = [names] if names else []
    out, seen = [], set()
    for _n in (names or []):
        _k = _name_to_key(_n, participants)
        if not _k or _k in seen:
            continue
        for _p in participants:
            if _p["key"] == _k:
                out.append(_p)
                seen.add(_k)
                break
    return out

'''
    text = text.replace(a1, b1, 1)
    print("✔ 改动1：已插入 load_stage_assignments / _name_to_key / _names_to_parts")

    # ── 改动 2：run_mesh_phase 里读角色 ──
    a2 = '    parts = sess["participants"]\n    merger = sess["merge_app"]\n    out_dir = phase_dir(program, chapter, phase_cfg["key"])\n'
    if a2 not in text:
        print("[失败] 找不到 run_mesh_phase 开头")
        return
    b2 = '''    parts = sess["participants"]
    merger = sess["merge_app"]

    # _roles_from_stage_board：读 UI 指派
    _assign = load_stage_assignments()
    _stage_a = _assign.get(program, {}).get("steps", {})
    _this_a = _stage_a.get(phase_cfg["key"], {}) or {}

    _exec_names = (_this_a.get("blocks", {}) or {}).get("产出") or []
    _rev_names = _this_a.get("reviewer") or []
    _adj_name = _this_a.get("adjuster") or ""

    phase_writers = _names_to_parts(_exec_names, parts) or parts
    phase_reviewers = _names_to_parts(_rev_names, parts) or parts
    phase_merger = None
    if _adj_name:
        _adj_key = _name_to_key(_adj_name, parts)
        for _p in parts:
            if _p["key"] == _adj_key:
                phase_merger = _p
                break
    if not phase_merger:
        phase_merger = merger

    print(f"  [角色] 执行={[p['label'] for p in phase_writers]} "
          f"审核={[p['label'] for p in phase_reviewers]} "
          f"调整={phase_merger['label']}")

    out_dir = phase_dir(program, chapter, phase_cfg["key"])
'''
    text = text.replace(a2, b2, 1)
    print("✔ 改动2：run_mesh_phase 里读角色")

    # ── 改动 3：writers 用 phase_writers ──
    a3 = "        writers = parts[:1] if once else parts\n"
    if a3 not in text:
        print("[失败] 找不到 writers = 那一行")
        return
    text = text.replace(a3, "        writers = phase_writers[:1] if once else phase_writers\n", 1)
    print("✔ 改动3：writers 用 phase_writers")

    # ── 改动 4：reviews 循环用 phase_reviewers ──
    a4 = '''        reviews = []
        for v in versions:
            writer_key = v.stem.split("__")[-1]
            for r in parts:
                if r["key"] == writer_key:
                    continue'''
    if a4 not in text:
        print("[失败] 找不到 reviews 循环")
        return
    b4 = a4.replace("for r in parts:", "for r in phase_reviewers:")
    text = text.replace(a4, b4, 1)
    print("✔ 改动4：reviews 循环用 phase_reviewers")

    # ── 改动 5：do_merge 用 phase_merger ──
    a5 = '''        if len(versions) >= 2:
            do_merge(agent, sess, merger, program, phase_cfg, cid, clabel,
                     versions, reviews, out_dir, dry)'''
    if a5 not in text:
        print("[失败] 找不到 do_merge 调用")
        return
    b5 = a5.replace("sess, merger,", "sess, phase_merger,")
    text = text.replace(a5, b5, 1)
    print("✔ 改动5：do_merge 用 phase_merger")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()