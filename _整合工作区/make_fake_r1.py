from pathlib import Path

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")

# 造假 R1_润色产出（供质检读）
r1_dir = proj_root / "03_去AI" / "R1_润色" / "versions"
r1_dir.mkdir(parents=True, exist_ok=True)
for ch in [1, 2, 5]:
    f = r1_dir / f"R1_润色__workbuddy__章{ch}.md"
    f.write_text(f"# 第{ch}章润色后正文\n\n这是润色后的第{ch}章内容……\n", encoding="utf-8")
    print(f"已造：{f.name}")
