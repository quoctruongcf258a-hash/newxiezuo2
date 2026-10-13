# fix_send_wait.py — 延长粘贴后等待 + 发送后验证重试
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''        # 5. 发送（QUEST=Ctrl+Enter，其他=Enter）
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

NEW = '''        # 5. 发送（延长等待 + 发送后验证重试）
        # 4200 字 prompt 粘贴后 1.2 秒按回车，AI 界面可能还在处理粘贴，回车会被吞
        time.sleep(3.0)
        _mods = 2 if ai == "QUEST" else 0

        def _try_send():
            self.cmd("Input.dispatchKeyEvent", type="rawKeyDown",
                     windowsVirtualKeyCode=13, code="Enter", key="Enter", modifiers=_mods)
            time.sleep(0.08)
            self.cmd("Input.dispatchKeyEvent", type="char", text="\\r", modifiers=_mods)
            time.sleep(0.08)
            self.cmd("Input.dispatchKeyEvent", type="keyUp",
                     windowsVirtualKeyCode=13, code="Enter", key="Enter", modifiers=_mods)
            time.sleep(1.5)

        _try_send()
        # 发送后验证：输入框仍 >100 字说明没发出去，再试
        for _attempt in range(3):
            try:
                _left = self.js(_LEFT_JS)
            except Exception:
                _left = 0
            if not _left or _left < 100:
                break
            print(f"[send] 输入框仍有 {_left} 字，第 {_attempt+2} 次重发...")
            time.sleep(1.0)
            _try_send()
        time.sleep(0.5)
'''

if "延长等待 + 发送后验证重试" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
    i = text.find("# 5. 发送")
    if i >= 0:
        print(repr(text[i:i+500]))
else:
    bak = TARGET.with_suffix(".py.bak_sendwait")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已改：粘贴后等 3 秒 + 发送后验证重试")