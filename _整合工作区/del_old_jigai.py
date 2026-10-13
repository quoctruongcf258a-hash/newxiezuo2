# del_old_jigai.py — 备份 + 删除旧 第0步梗概.md
import shutil
from pathlib import Path

INIT = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test\00_初始化")
target = INIT / "第0步梗概.md"
bak = INIT / "第0步梗概.md.bak_old"

if not target.exists():
    print(f"文件不存在：{target}")
else:
    if not bak.exists():
        shutil.copy(target, bak)
        print(f"OK 已备份：{bak.name}")
    else:
        print(f"备份已存在：{bak.name}")

    target.unlink()
    print(f"OK 已删除：{target.name}")

print()
print("=== 现在 00_初始化 下 ===")
for p in sorted(INIT.iterdir()):
    if p.is_file():
        print(f"  {p.name}  ({p.stat().st_size} 字节)")