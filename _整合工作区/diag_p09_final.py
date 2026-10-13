from pathlib import Path
import json

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
p09 = proj_root / "01_规划" / "全书结构"

print("=" * 70)
print("P09 完整目录结构")
print("=" * 70)
if p09.exists():
    for item in sorted(p09.rglob("*")):
        rel = item.relative_to(p09)
        if item.is_dir():
            print(f"  📁 {rel}/")
        else:
            print(f"  📄 {rel}  ({item.stat().st_size}B)")
else:
    print(f"  ❌ 不存在")

print()
print("=" * 70)
print("versions/ 各 AI 目录内容")
print("=" * 70)
versions = p09 / "versions"
if versions.exists():
    for d in sorted(versions.iterdir()):
        if d.is_dir():
            files = list(d.glob("*"))
            print(f"\n  📁 {d.name}/  ({len(files)} 文件)")
            for f in files:
                print(f"     📄 {f.name}  ({f.stat().st_size}B)")
        else:
            print(f"  📄 {d.name}  (不是目录)")
else:
    print("  ❌ versions/ 不存在")

print()
print("=" * 70)
print("_failed/ 目录")
print("=" * 70)
failed = proj_root / "_failed"
if failed.exists():
    for f in sorted(failed.rglob("*")):
        if f.is_file():
            print(f"  📄 {f.relative_to(failed)}")
            if f.suffix == ".json":
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    print(f"     内容：{json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                except Exception:
                    pass
else:
    print("  ✅ 无 _failed/")

print()
print("=" * 70)
print("split.json")
print("=" * 70)
split = p09 / "split.json"
if split.exists():
    print(split.read_text(encoding="utf-8"))
else:
    print("  ❌ 不存在")
