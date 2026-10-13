# probe_init_deps.py — 查 00_初始化 被哪些地方依赖
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
INIT = BASE / "output" / "女王归来_test" / "00_初始化"
SCRATCH = BASE / "windows-use" / "_scratch"

# 1. 看 00_初始化 现有文件
print("=" * 60)
print("1) 00_初始化 现有文件")
print("=" * 60)
if INIT.exists():
    for p in sorted(INIT.iterdir()):
        if p.is_file():
            print(f"  {p.name}  ({p.stat().st_size} 字节)")
else:
    print("  不存在:", INIT)

# 2. 看 第0步梗概.md 内容
print()
print("=" * 60)
print("2) 第0步梗概.md 内容")
print("=" * 60)
p = INIT / "第0步梗概.md"
if p.exists():
    print(p.read_text(encoding="utf-8"))
else:
    print("  不存在")

# 3. orchestrator.py 里所有引用 00_初始化 / 1.0~1.6 的地方
print()
print("=" * 60)
print("3) orchestrator.py 里的引用")
print("=" * 60)
O = SCRATCH / "orchestrator.py"
text = O.read_text(encoding="utf-8")
for i, ln in enumerate(text.splitlines(), 1):
    if any(k in ln for k in ["00_初始化", "1.0_总纲", "1.1_定位", "1.2_故事",
                              "1.3_人物", "1.4_世界观", "1.5_结构", "1.6_卷纲",
                              "_parse_volumes", "第0步梗概"]):
        print(f"{i:4d}| {ln[:140]}")

# 4. 项目信息.json 内容
print()
print("=" * 60)
print("4) 项目信息.json")
print("=" * 60)
import json
p2 = INIT / "项目信息.json"
if p2.exists():
    d = json.loads(p2.read_text(encoding="utf-8"))
    for k, v in d.items():
        print(f"  {k} = {str(v)[:80]}")