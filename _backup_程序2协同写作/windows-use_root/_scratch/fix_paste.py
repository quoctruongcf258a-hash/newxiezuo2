fp = r"C:\mai\multi-ai-pipeline\windows-use\mix_send.py"
with open(fp, "r", encoding="utf-8") as f:
    t = f.read()

old = '''        # 4. 真输入（逐字符，让 Slate/React 同步 state）
        for ch in text:
            self.cmd("Input.insertText", text=ch)
            time.sleep(0.015)
        time.sleep(1.2)'''

new = '''        # 4. 用剪贴板粘贴（对 Slate 有效）
        import pyperclip
        pyperclip.copy(text)
        time.sleep(0.3)
        # Ctrl+V
        self.cmd("Input.dispatchKeyEvent", type="rawKeyDown", windowsVirtualKeyCode=86, code="KeyV", key="v", modifiers=2)
        time.sleep(0.05)
        self.cmd("Input.dispatchKeyEvent", type="char", text="v", modifiers=2)
        time.sleep(0.05)
        self.cmd("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=86, code="KeyV", key="v", modifiers=2)
        time.sleep(1.2)'''

if old in t:
    t = t.replace(old, new)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(t)
    print("✅ 改成剪贴板粘贴")
else:
    print("❌ 没找到目标")
