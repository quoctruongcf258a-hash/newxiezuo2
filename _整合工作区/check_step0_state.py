# check_step0_state.py — 看 00_初始化 现在有什么
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
INIT = BASE / "output" / "女王归来_test" / "00_初始化"

print("=" * 60)
print(f"目录: {INIT}")
print("=" * 60)
if not INIT.exists():
    print("  目录不存在")
else:
    for p in sorted(INIT.iterdir()):
        if p.is_file():
            t = p.read_text(encoding="utf-8", errors="ignore")
            print(f"  {p.name}")
            print(f"    字节: {p.stat().st_size}")
            print(f"    前 120 字: {t[:120]!r}")
            print()