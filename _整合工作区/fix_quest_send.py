# fix_quest_send.py — QUEST 用 Ctrl+Enter 发送（IDE 风格输入框）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''        # 5. 先回车
        self.cmd("Input.dispatchKeyEvent", type="rawKeyDown", windowsVirtualKeyCode=13, code="Enter", key="Enter")
        time.sleep(0.05)
        self.cmd("Input.dispatchKeyEvent", type="char", text="\\r")
        time.sleep(0.05)
        self.cmd("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=13, code="Enter", key="Enter")
        time.sleep(1.2)
'''

NEW = '''        # 5. 发送（QUEST=Ctrl+Enter，其他=Enter）
        # IDE 风格输入框：Enter 是换行，Ctrl+Enter 才发送
        _mods = 2 if ai == "QUEST" else 0
        self.cmd("Input.dispatchKeyEvent", type="rawKeyDown",
                 windowsVirtualKeyCode=13, code="Enter", key="Enter", modifiers=_mods)
        time.sleep(0.05)
        self.cmd("Input.dispatchKeyEvent", type="char", text="\\r", modifiers=_mods)
        time.sleep(0.05)
        self.cmd("Input.dispatchKeyEvent", type="keyUp",
                 windowsVirtualKeyCode=13, code="Enter", key="Enter", modifiers=_mods)
        time.sleep(1.2)
'''

if "QUEST=Ctrl+Enter" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
    i = text.find("# 5. 先回车")
    if i >= 0:
        print(repr(text[i:i+500]))
else:
    bak = TARGET.with_suffix(".py.bak_questsend")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ QUEST 已改成 Ctrl+Enter 发送")