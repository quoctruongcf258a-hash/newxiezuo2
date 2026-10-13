# show_p01_p02.py — 看 P01、P02、_通用 的实际内容
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
P = BASE / "prompts" / "01_规划"

for name in ["_通用.md", "P01.md", "P02.md", "P03.md", "P04.md", "P05.md"]:
    f = P / name
    print("=" * 70)
    print(f"文件: {name}  ({f.stat().st_size if f.exists() else 0} 字节)")
    print("=" * 70)
    if f.exists():
        print(f.read_text(encoding="utf-8"))
    else:
        print("(不存在)")
    print()