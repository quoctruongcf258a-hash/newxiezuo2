fp = r"C:\mai\multi-ai-pipeline\windows-use\mix_send.py"
with open(fp, "r", encoding="utf-8") as f:
    t = f.read()

# 找 send_text 方法整体，定位"5. 纯回车"到方法结尾
marker = "        # 5. 纯回车"
idx = t.find(marker)
if idx == -1:
    print("找不到 5. 纯回车")
    exit()

# 从 5. 纯回车 开始，找到下一个"return f"剩余="
end_marker = 'return f"剩余={left}"'
end_idx = t.find(end_marker, idx)
if end_idx == -1:
    print("找不到 return 剩余")
    exit()
end_idx += len(end_marker)

# 新的收尾段
new_tail = '''        # 5. 先回车
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
                return f"剩余={_left()} (按钮兜底)"
        return f"剩余={left}"'''

# 替换
t2 = t[:idx] + new_tail + t[end_idx:]

with open(fp, "w", encoding="utf-8") as f:
    f.write(t2)
print("✅ 已加按钮兜底")
