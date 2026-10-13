# show_p01p02.py — 看 _通用 P01 P02 P06-01
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
P = BASE / "prompts" / "01_规划"

for name in ["_通用.md", "P01.md", "P02.md", "P06-01.md", "P09.md", "P16.md"]:
    f = P / name
    print("=" * 70)
    print(f"文件: {name}")
    print("=" * 70)
    if f.exists():
        print(f.read_text(encoding="utf-8"))
    else:
        print("(不存在)")
    print()