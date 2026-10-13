from pathlib import Path
import shutil

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")

# 1. 删 P09 产出
p09 = proj_root / "01_规划" / "全书结构"
if p09.exists():
    shutil.rmtree(p09)
    print(f"✅ 已删：01_规划/全书结构/")

# 2. 删 _progress（步骤号重置为 1）
progress = proj_root / "_progress"
if progress.exists():
    shutil.rmtree(progress)
    print(f"✅ 已删：_progress/")

# 3. 删 _failed
failed = proj_root / "_failed"
if failed.exists():
    shutil.rmtree(failed)
    print(f"✅ 已删：_failed/")

# 4. 清任务文件
task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
if task_dir.exists():
    cnt = 0
    for f in task_dir.glob("task__*.md"):
        f.unlink()
        cnt += 1
    print(f"✅ 已删 {cnt} 个任务文件")

# 5. 清 pyc
cnt = 0
for pyc_dir in Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use").rglob("__pycache__"):
    shutil.rmtree(pyc_dir)
    cnt += 1
print(f"✅ 已删 {cnt} 个 __pycache__")
