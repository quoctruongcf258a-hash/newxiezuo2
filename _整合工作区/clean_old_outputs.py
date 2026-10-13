from pathlib import Path

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
import shutil

# 删所有 phases 的 versions 目录
count = 0
for ver_dir in proj_root.rglob("versions"):
    if ver_dir.is_dir():
        shutil.rmtree(ver_dir)
        count += 1
        print(f"  已删：{ver_dir.relative_to(proj_root)}")

# 删 _failed
failed_dir = proj_root / "_failed"
if failed_dir.exists():
    shutil.rmtree(failed_dir)
    print(f"  已删：_failed/")

print(f"\n共清理 {count} 个 versions/ 目录")
