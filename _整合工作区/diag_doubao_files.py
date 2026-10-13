from pathlib import Path
import time

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
p09 = proj_root / "01_规划" / "全书结构"

print("=" * 70)
print("P09 实际产出目录")
print("=" * 70)
if p09.exists():
    for item in sorted(p09.rglob("*")):
        rel = item.relative_to(p09)
        if item.is_dir():
            print(f"  📁 {rel}/")
        else:
            t = time.strftime("%H:%M:%S", time.localtime(item.stat().st_mtime))
            print(f"  📄 [{t}] {rel}  ({item.stat().st_size}B)")

print()
print("=" * 70)
print("verify_fn 期望的路径")
print("=" * 70)
# 模拟 verify_fn 的路径计算
ai_dir = p09 / "versions" / "doubao"
print(f"  应该找：{ai_dir / '全书结构.md'}")
print(f"  实际存在：{(ai_dir / '全书结构.md').exists()}")

# 列出 doubao 目录所有文件
if ai_dir.exists():
    print(f"\n  doubao/ 目录实际内容：")
    for f in ai_dir.glob("*"):
        print(f"    {f.name}  ({f.stat().st_size}B)")
