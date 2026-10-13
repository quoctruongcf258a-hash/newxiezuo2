from pathlib import Path

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")

# 造 P18 前30章落地章纲的假产出
p18_dir = proj_root / "01_规划" / "前30章落地章纲" / "versions"
p18_dir.mkdir(parents=True, exist_ok=True)
for ch in [1, 2, 5]:
    f = p18_dir / f"前30章落地章纲__workbuddy__章{ch}.md"
    f.write_text(f"# 第{ch}章落地章纲\n目标：主角做某事\n阻力：遇到某人\n", encoding="utf-8")
    print(f"已造：{f.name}")

# 造 W0 的假产出（供 W1 测试）
w0_dir = proj_root / "02_写作" / "W0_细纲分析" / "versions"
w0_dir.mkdir(parents=True, exist_ok=True)
for ch in [1, 2, 5]:
    f = w0_dir / f"W0_细纲分析__workbuddy__章{ch}.md"
    f.write_text(f"# 第{ch}章细纲分析\n本章一句话：主角在城中遇到危机\n目标：过关\n", encoding="utf-8")
    print(f"已造：{f.name}")
