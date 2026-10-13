fp = r"C:\mai\multi-ai-pipeline\windows-use\mix_send.py"
with open(fp, "r", encoding="utf-8") as f:
    t = f.read()

# 找 send_text 里"纯回车"部分，改成"回车→检查→按钮兜底"
old = '''        # 5. 纯回车
        self.cmd("Input.dispatchKeyEvent", type="rawKeyDown", windowsVirtualKeyCode=13, code="Enter", key="Enter")
        time.sleep(0.05)
        self.cmd("Input.dispatchKeyEvent", type="char", text="\\r")
        time.sleep(0.05)
        self.cmd("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=13, code="Enter", key="Enter")
        time.sleep(1.5)
        # 6. 检查剩余
        left = self.js("""
        (() => {
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return -1;
            return el.value !== undefined ? el.value.length : el.textContent.length;
        })()
        """)
        return f"剩余={left}"'''

new = '''        # 5. 先回车
        self.cmd("Input.dispatchKeyEvent", type="rawKeyDown", windowsVirtualKeyCode=13, code="Enter", key="Enter")
        time.sleep(0.05)
        self.cmd("Input.dispatchKeyEvent", type="char", text="\\r")
        time.sleep(0.05)
        self.cmd("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=13, code="Enter", key="Enter")
        time.sleep(1.2)

        def _left():
            return self.js("""
            (() => {
                const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
                if (!el) return -1;
                const slate = el.querySelector('[data-slate-string="true"]');
                if (slate) return slate.textContent.length;
                return el.value !== undefined ? el.value.length : (el.textContent || "").trim().length;
            })()
            """)

        left = _left()

        # 6. 回车没清空 → 找按钮点击
        if left > 0:
            btn = self.js("""
            (() => {
                const btns = [...document.querySelectorAll('button, [role="button"]')];
                let b = btns.find(x => {
                    const a = (x.getAttribute('aria-label')||'').trim();
                    return a === '发送' || a === '发送消息' || a === 'Send message' || a === 'Send';
                });
                if (!b) b = document.querySelector('.cr-send-button, .chat-input-v2-send-button');
                if (!b) return null;
                if (b.disabled) return {disabled: true};
                const r = b.getBoundingClientRect();
                return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
            })()
            """)
            if btn and not btn.get("disabled"):
                self.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=btn["x"], y=btn["y"])
                time.sleep(0.1)
                self.cmd("Input.dispatchMouseEvent", type="mousePressed", x=btn["x"], y=btn["y"], button="left", clickCount=1)
                time.sleep(0.08)
                self.cmd("Input.dispatchMouseEvent", type="mouseReleased", x=btn["x"], y=btn["y"], button="left", clickCount=1)
                time.sleep(1.5)
                left = _left()
                return f"剩余={left} (按钮兜底)"
        return f"剩余={left}"'''

if old in t:
    t = t.replace(old, new)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(t)
    print("✅ mix_send 已加按钮兜底")
else:
    print("❌ 没找到目标")
    idx = t.find("5. 纯回车")
    if idx >= 0:
        print(t[idx-200:idx+500])
