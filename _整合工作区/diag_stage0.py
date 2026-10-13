from pathlib import Path
import json

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
init_dir = proj_root / "00_初始化"

print("=== 00_初始化 目录内容 ===")
if not init_dir.exists():
    print(f"  ❌ 目录不存在：{init_dir}")
    raise SystemExit(0)

for f in sorted(init_dir.rglob("*")):
    rel = f.relative_to(init_dir)
    if f.is_dir():
        print(f"  📁 {rel}/")
    else:
        size = f.stat().st_size
        print(f"  📄 {rel}  ({size}B)")

# 各文件的顶层结构/前 200 字
print("\n=== 各文件内容摘要 ===")
for f in sorted(init_dir.rglob("*.json")):
    print(f"\n--- {f.name} ---")
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for k, v in list(data.items())[:15]:
                if isinstance(v, (list, dict)):
                    print(f"  {k}: {type(v).__name__} ({len(v)} 项)")
                else:
                    print(f"  {k}: {repr(v)[:80]}")
        else:
            print(f"  {type(data).__name__}, 前 200 字符：{str(data)[:200]}")
    except Exception as e:
        print(f"  解析失败：{e}")

for f in sorted(init_dir.rglob("*.md")):
    print(f"\n--- {f.name} ---")
    text = f.read_text(encoding="utf-8", errors="ignore")
    print(f"  总长 {len(text)} 字")
    print(f"  前 300 字：\n{text[:300]}")

# 检查 rings_items.json 里有没有 00_初始化 定义
print("\n\n=== rings_items.json 里有没有 00_初始化 ===")
rings_path = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json")
rings = json.loads(rings_path.read_text(encoding="utf-8"))
print(f"  顶层键：{list(rings.keys())}")
for k in rings.keys():
    if "初始化" in k or "0" in k:
        print(f"  ★ 找到：{k}")

# 检查 apps.json 里有没有 00_初始化 阶段
print("\n=== apps.json 里有没有 00_初始化 ===")
apps_path = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\apps.json")
if apps_path.exists():
    apps = json.loads(apps_path.read_text(encoding="utf-8"))
    print(f"  顶层键：{list(apps.keys())[:20]}")
    for k in apps.keys():
        if "初始化" in k or "init" in k.lower():
            print(f"  ★ 找到：{k}")

# 检查 orchestrator.py 里有没有处理 00_初始化 的逻辑
print("\n=== orchestrator.py 里提到 00_初始化 的行 ===")
orch = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = orch.read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(lines):
    if "00_初始化" in ln:
        print(f"  {i+1:4d}| {ln.strip()[:100]}")
