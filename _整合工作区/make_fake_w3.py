from pathlib import Path

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")

# 造假的 W3 正文（供润色读）
w3_dir = proj_root / "02_写作" / "W3_正文" / "versions"
w3_dir.mkdir(parents=True, exist_ok=True)
for ch in [1, 2, 5]:
    f = w3_dir / f"W3_正文__workbuddy__章{ch}.md"
    f.write_text(f"# 第{ch}章正文\n\n这是主角在第{ch}章的故事……\n", encoding="utf-8")
    print(f"已造：{f.name}")
