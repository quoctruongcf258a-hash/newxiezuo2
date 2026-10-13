# show_init_dir.py — 看 00_初始化 目录全貌 + 801-830 行逻辑
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
init_dir = BASE / "output" / "女王归来" / "00_初始化"

print("=" * 30, "00_初始化 目录全部文件", "=" * 30)
if init_dir.exists():
    for p in sorted(init_dir.rglob("*")):
        rel = p.relative_to(init_dir)
        if p.is_file():
            print(f"  {rel}  ({p.stat().st_size} 字节)")
        else:
            print(f"  {rel}/")
else:
    print("  目录不存在:", init_dir)

print()
print("=" * 30, "orchestrator.py 第 795-835 行", "=" * 30)
P = BASE / "windows-use" / "_scratch" / "orchestrator.py"
lines = P.read_text(encoding="utf-8").splitlines()
for i in range(794, 835):
    if i < len(lines):
        print(f"{i+1:4d}| {lines[i]}")