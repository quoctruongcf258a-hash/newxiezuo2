# fix_all_filemode.py — 4 个 AI 全走文件模式
import shutil
from pathlib import Path

T = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = T.read_text(encoding="utf-8")

OLD = 'FILE_MODE_AIS = {"QUEST"}'
NEW = 'FILE_MODE_AIS = {"QUEST", "WorkBuddy", "Doubao", "gemini"}'

if NEW in text:
    print("已改过")
elif OLD in text:
    bak = T.with_suffix(".py.bak_allfile")
    if not bak.exists():
        shutil.copy(T, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    T.write_text(text, encoding="utf-8")
    print("✔ 4 个 AI 全走文件模式")
else:
    print("找不到 FILE_MODE_AIS")