# show_init_block.py — 看 orchestrator.py 第 790-860 行（00_初始化读取逻辑）
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "第 790-870 行", "=" * 30)
for i in range(789, 870):
    if i < len(lines):
        print(f"{i+1:4d}| {lines[i]}")

print()
print("=" * 30, "phases.json / rings_items.json 里有没有 00_初始化", "=" * 30)
import json
BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
for name in ["rules/phases.json", "rules/rings_items.json"]:
    p = BASE / name
    if not p.exists():
        print(f"  {name}: 不存在")
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    keys = list(d.keys()) if isinstance(d, dict) else "list"
    print(f"  {name}: keys={keys}")

print()
print("=" * 30, "项目信息.json 全文", "=" * 30)
pinfo = BASE / "output" / "女王归来" / "00_初始化" / "项目信息.json"
print(pinfo.read_text(encoding="utf-8"))