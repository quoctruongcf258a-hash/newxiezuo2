# fix_proj_path.py — 修正 PROJECT_FILE 路径
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = 'PROJECT_FILE = HERE.parent / "work" / "collab" / "current_project.json"\n'
NEW = 'PROJECT_FILE = HERE.parent.parent / "work" / "collab" / "current_project.json"\n'

text = TARGET.read_text(encoding="utf-8")

if NEW in text:
    print("已改过")
elif OLD not in text:
    print("找不到 PROJECT_FILE 那一行")
else:
    bak = TARGET.with_suffix(".py.bak_projfix")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已修正 PROJECT_FILE 路径")