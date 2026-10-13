from pathlib import Path

# 1. 看 P09 产出目录里实际有什么文件
proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
p09 = proj_root / "01_规划" / "全书结构"
print("=" * 70)
print("P09 versions/ 实际文件")
print("=" * 70)
if p09.exists():
    for f in sorted(p09.rglob("*")):
        rel = f.relative_to(p09)
        if f.is_file():
            print(f"  📄 {rel}  ({f.stat().st_size}B)")

# 2. 看最新 task 文件的"输出位置"
task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
files = sorted(task_dir.glob("*全书结构*.md"), key=lambda f: f.stat().st_mtime)
if files:
    latest = files[-1]
    txt = latest.read_text(encoding="utf-8", errors="ignore")
    i = txt.find("## 输出位置")
    if i >= 0:
        print(f"\n最新 task 文件的输出位置：")
        print(txt[i:i+300])
