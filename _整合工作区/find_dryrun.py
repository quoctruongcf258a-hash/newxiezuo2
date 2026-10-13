from pathlib import Path

root = Path(r"F:\赛马23环整合工作室")

print("=== 搜索 dry_run 相关脚本 ===")
for p in root.rglob("*.py"):
    name = p.name.lower()
    if any(k in name for k in ["dry", "run", "gen", "expand", "phase", "test"]):
        print(f"  {p.relative_to(root)}")

print("\n=== 搜索已有的 _v*.txt 文件 ===")
found = False
for p in root.rglob("_v*.txt"):
    print(f"  {p.relative_to(root)}")
    found = True
if not found:
    print("  (全盘未找到 _v*.txt)")

print("\n=== 搜索所有 .py 脚本（前50个）===")
py_files = list(root.rglob("*.py"))
print(f"共 {len(py_files)} 个 py 文件")
for p in py_files[:50]:
    print(f"  {p.relative_to(root)}")
