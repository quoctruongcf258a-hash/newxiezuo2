from pathlib import Path
import os

task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
if task_dir.exists():
    # 找最近的几个任务文件
    files = sorted(task_dir.glob("*.md"), key=os.path.getmtime)
    print(f"共 {len(files)} 个任务文件，最近 3 个：")
    for f in files[-3:]:
        print(f"\n{'='*70}")
        print(f"📄 {f.name}  ({f.stat().st_size}B)")
        print('='*70)
        txt = f.read_text(encoding="utf-8", errors="ignore")
        # 判断是新格式还是旧格式
        if txt.startswith("# 任务："):
            print("[新格式]")
            print(txt[:600])
        else:
            print("[旧格式]")
            print(txt[:600])
