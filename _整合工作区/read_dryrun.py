from pathlib import Path

# dryrun_to_file.py 的候选位置
candidates = [
    Path(r"F:\赛马23环整合工作室\_整合工作区\dryrun_to_file.py"),
    Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\dryrun_to_file.py"),
]

found = None
for p in candidates:
    if p.exists():
        found = p
        break

if not found:
    print("❌ 在候选位置找不到 dryrun_to_file.py，全盘搜索中...")
    for p in Path(r"F:\赛马23环整合工作室").rglob("dryrun_to_file.py"):
        if ".venv" in str(p) or "site-packages" in str(p):
            continue
        print(f"  找到: {p}")
        found = p
        break

if found:
    print(f"\n=== 读取 {found} ===\n")
    text = found.read_text(encoding="utf-8")
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        print(f"{i+1:4d}| {ln}")
    print(f"\n=== 共 {len(lines)} 行 ===")
