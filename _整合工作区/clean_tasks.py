from pathlib import Path
task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
if task_dir.exists():
    cnt = 0
    for f in task_dir.glob("task__*.md"):
        f.unlink()
        cnt += 1
    print(f"已删 {cnt} 个任务文件")
