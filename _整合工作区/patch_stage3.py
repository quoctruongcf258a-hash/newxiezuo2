import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

changed = 0

# ── 补丁 A：chunks_for_phase 顶部加"走拆分引擎的环节返回单块" ──
OLD_A = '''def chunks_for_phase(cfg, program, phase_cfg) -> list:
    """把一个环节切成若干「块」。返回 [(chunk_id, chunk_label, standard_block), ...]

    规划：环节即块（desc 作为说明）；P16 volume 按卷纲切，P17 chapters 按 segment_size 切
    写作：分布/正文 按六要素切 6 块；其余环节单块
    润色：按 4 节切
    质检：按 qcSecs 每节一块
    """
    key = phase_cfg["key"]

    # P16：按卷切（从 1.6_卷纲.md 读真实区间）'''

NEW_A = '''def chunks_for_phase(cfg, program, phase_cfg) -> list:
    """把一个环节切成若干「块」。返回 [(chunk_id, chunk_label, standard_block), ...]

    规划：环节即块（desc 作为说明）；P16 volume 按卷纲切，P17 chapters 按 segment_size 切
    写作：分布/正文 按六要素切 6 块；其余环节单块
    润色：按 4 节切
    质检：按 qcSecs 每节一块
    """
    key = phase_cfg["key"]

    # 走拆分引擎的环节：单块，让 _get_split_spec 接管
    _name = phase_cfg.get("name") or phase_cfg.get("key") or ""
    if _name in SPLIT_SOURCES:
        return [(key, key, "")]

    # P16：按卷切（从 1.6_卷纲.md 读真实区间）'''

if OLD_A in text:
    text = text.replace(OLD_A, NEW_A, 1)
    print("[OK] A：chunks_for_phase 加拆分引擎短路")
    changed += 1
else:
    print("[FAIL] A 找不到锚点")

# ── 补丁 B：SPLIT_SOURCES 加润色 ──
OLD_B = '''    "W4_章内节奏自检":  ("01_规划/粗纲规划", "current_stage_split"),
}'''

NEW_B = '''    "W4_章内节奏自检":  ("01_规划/粗纲规划", "current_stage_split"),
    # ── 润色阶段（读 02_写作/W3_正文 的同章产出）──
    "R1_润色":          ("02_写作/W3_正文", "current_stage_split"),
}'''

if OLD_B in text:
    text = text.replace(OLD_B, NEW_B, 1)
    print("[OK] B：SPLIT_SOURCES 加润色")
    changed += 1
else:
    print("[FAIL] B 找不到锚点")

# ── 补丁 C：_read_upstream_for_chapter 加润色支持 ──
OLD_C = '''    if program == "写作" and name in WRITE_ORDER:
        write_root = od.parent          # .../02_写作/
        cur_idx = WRITE_ORDER.index(name)'''

NEW_C = '''    # ── 润色：读 02_写作/W3_正文 的同章产出 ──
    if program == "润色" and "润色" in name:
        proj_root = od.parent.parent     # .../03_去AI/R1_润色 → 项目根
        w3_dir = proj_root / "02_写作" / "W3_正文" / "versions"
        if w3_dir.exists():
            for f in sorted(w3_dir.glob(f"*__章{chapter_no}.md")):
                try:
                    c = f.read_text(encoding="utf-8", errors="ignore")
                    if len(c) > 8000:
                        c = c[:8000] + f"\\n…（已截断，全文 {len(c)} 字）"
                    parts.append(f"【上游：W3_正文 第{chapter_no}章（{f.name}）】\\n{c}")
                except Exception:
                    pass

    if program == "写作" and name in WRITE_ORDER:
        write_root = od.parent          # .../02_写作/
        cur_idx = WRITE_ORDER.index(name)'''

if OLD_C in text:
    text = text.replace(OLD_C, NEW_C, 1)
    print("[OK] C：_read_upstream_for_chapter 加润色")
    changed += 1
else:
    print("[FAIL] C 找不到锚点")

# ── 写回 ──
if changed >= 2:
    bak = TARGET.with_suffix(".py.bak_stage3")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回（{changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处，未写回")
