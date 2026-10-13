from pathlib import Path
import shutil

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")

# 删 P09 产出
p09 = proj_root / "01_规划" / "全书结构"
if p09.exists():
    shutil.rmtree(p09)
    print(f"已删：01_规划/全书结构/")

# 清 _failed
failed = proj_root / "_failed"
if failed.exists():
    shutil.rmtree(failed)
    print(f"已删：_failed/")

# 清旧任务文件
task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
if task_dir.exists():
    cnt = 0
    for f in task_dir.glob("task__*.md"):
        f.unlink()
        cnt += 1
    print(f"已删 {cnt} 个旧任务文件")

# 清 pyc 缓存（避免补丁不生效）
import py_compile
for p in (Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")).rglob("__pycache__"):
    shutil.rmtree(p)
    print(f"已删缓存：{p.name}")
