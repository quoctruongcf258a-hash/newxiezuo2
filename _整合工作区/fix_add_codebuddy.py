import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

OLD = 'FILE_MODE_AIS = {"quest", "workbuddy", "doubao", "gemini"}'
NEW = 'FILE_MODE_AIS = {"quest", "workbuddy", "doubao", "gemini", "codebuddy"}'

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_addcb")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已把 codebuddy 加入 FILE_MODE_AIS")
elif "codebuddy" in text and "FILE_MODE_AIS" in text:
    print("[SKIP] 已包含 codebuddy")
else:
    print("[FAIL] 找不到 FILE_MODE_AIS 定义")
