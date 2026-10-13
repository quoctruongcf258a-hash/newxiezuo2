# show_step0.py — 看步骤0的提示词内容
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

for path in [
    "prompts/步骤0/no0tisc.md",
    "prompts/00_初始化/_通用.md",
    "prompts/00_初始化/故事梗概.md",
]:
    f = BASE / path
    print("=" * 75)
    print(f"📄 {path}  ({f.stat().st_size if f.exists() else 0} 字节)")
    print("=" * 75)
    if f.exists():
        print(f.read_text(encoding="utf-8"))
    else:
        print("(不存在)")
    print()