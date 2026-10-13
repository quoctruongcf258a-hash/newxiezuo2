import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

changed = 0

# ── 补丁 A：SPLIT_SOURCES 加 7 个质检环 ──
OLD_A = '''    # ── 润色阶段（读 01_规划/粗纲规划 的章列表，按当前阶段过滤）──
    "R1_润色":          ("01_规划/粗纲规划", "current_stage_split"),
}'''

NEW_A = '''    # ── 润色阶段（读 01_规划/粗纲规划 的章列表，按当前阶段过滤）──
    "R1_润色":          ("01_规划/粗纲规划", "current_stage_split"),
    # ── 质检阶段（读 01_规划/粗纲规划 的章列表，按当前阶段过滤）──
    "Q1_逻辑设定一致":     ("01_规划/粗纲规划", "current_stage_split"),
    "Q2_平台合规":         ("01_规划/粗纲规划", "current_stage_split"),
    "Q3_爽点节奏":         ("01_规划/粗纲规划", "current_stage_split"),
    "Q4_文风格式回查":     ("01_规划/粗纲规划", "current_stage_split"),
    "Q5_质检汇总":         ("01_规划/粗纲规划", "current_stage_split"),
    "Q7_上架前低级错误检查": ("01_规划/粗纲规划", "current_stage_split"),
    "Q9_推演下一章":       ("01_规划/粗纲规划", "current_stage_split"),
}'''

if OLD_A in text:
    text = text.replace(OLD_A, NEW_A, 1)
    print("[OK] A：SPLIT_SOURCES 加 7 个质检环")
    changed += 1
else:
    print("[FAIL] A 找不到锚点")

# ── 补丁 B：_read_upstream_for_chapter 加质检支持 ──
OLD_B = '''    # ── 润色：读 02_写作/W3_正文 的同章产出 ──
    if program == "润色" and "润色" in name:'''

NEW_B = '''    # ── 质检：读 03_去AI/R1_润色 的同章产出 ──
    if program == "质检" and name.startswith("Q"):
        proj_root = od.parent.parent
        r1_dir = proj_root / "03_去AI" / "R1_润色" / "versions"
        if r1_dir.exists():
            for f in sorted(r1_dir.glob(f"*__章{chapter_no}.md")):
                try:
                    c = f.read_text(encoding="utf-8", errors="ignore")
                    if len(c) > 8000:
                        c = c[:8000] + f"\\n…（已截断，全文 {len(c)} 字）"
                    parts.append(f"【上游：R1_润色 第{chapter_no}章（{f.name}）】\\n{c}")
                except Exception:
                    pass

    # ── 润色：读 02_写作/W3_正文 的同章产出 ──
    if program == "润色" and "润色" in name:'''

if OLD_B in text:
    text = text.replace(OLD_B, NEW_B, 1)
    print("[OK] B：_read_upstream_for_chapter 加质检")
    changed += 1
else:
    print("[FAIL] B 找不到锚点")

# ── 写回 ──
if changed >= 2:
    bak = TARGET.with_suffix(".py.bak_stage4")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回（{changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处，未写回")
