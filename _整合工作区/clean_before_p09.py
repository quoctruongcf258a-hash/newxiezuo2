from pathlib import Path
import shutil
proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
p09 = proj_root / "01_规划" / "全书结构"
if p09.exists():
    shutil.rmtree(p09)
    print(f"已删：{p09.relative_to(proj_root)}")
failed = proj_root / "_failed"
if failed.exists():
    shutil.rmtree(failed)
    print(f"已删：_failed/")
task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
if task_dir.exists():
    cnt = 0
    for f in task_dir.glob("task__*.md"):
        f.unlink()
        cnt += 1
    print(f"已删 {cnt} 个任务文件")
