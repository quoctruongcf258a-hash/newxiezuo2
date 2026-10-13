"""CDP 发送器 v4 —— 统一用真鼠标+真输入+多策略发送"""
import json, urllib.request, websocket, time, sys

APPS = {
    "CodeBuddy": (9223, ""),
    "QUEST":     (9224, ""),
    "TraeWork":  (9225, ""),
    "Qianwen":   (9226, "qianwen.com"),
    "WorkBuddy": (9227, ""),
    "ZCode":     (9228, ""),
    "DeepSeek":  (9222, "deepseek"),
    "Doubao":    (9229, ""),   # 真正的豆包（TraeWork 顶替的那个不算）
}

class Tab:
    def __init__(self, port, url_kw=""):
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
            pages = [t for t in json.load(f) if t.get("type")=="page"]
        target = None
        if url_kw:
            for p in pages:
                if url_kw in p.get("url",""): target = p; break
        if target is None and pages: target = pages[0]
        if not target: raise Exception(f"端口 {port} 无页面")
        self.ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
        self.mid = 0
        self.title = target.get("title","")

    def cmd(self, method, **params):
        self.mid += 1
        self.ws.send(json.dumps({"id":self.mid,"method":method,"params":params}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.mid: return r

    def js(self, code):
        r = self.cmd("Runtime.evaluate", expression=code, returnByValue=True)
        return r.get("result",{}).get("result",{}).get("value")

    def focus_input(self):
        box = self.js("""
        (() => {
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
        })()
        """)
        if not box: return False
        self.cmd("Input.dispatchMouseEvent", type="mousePressed", x=box["x"], y=box["y"], button="left", clickCount=1)
        self.cmd("Input.dispatchMouseEvent", type="mouseReleased", x=box["x"], y=box["y"], button="left", clickCount=1)
        time.sleep(0.3)
        # Ctrl+A 全选，Delete 清空
        self.cmd("Input.dispatchKeyEvent", type="rawKeyDown", windowsVirtualKeyCode=65, code="KeyA", key="a", modifiers=2)  # ctrl
        self.cmd("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=65, code="KeyA", key="a", modifiers=2)
        time.sleep(0.1)
        self.cmd("Input.dispatchKeyEvent", type="rawKeyDown", windowsVirtualKeyCode=46, code="Delete", key="Delete")
        self.cmd("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=46, code="Delete", key="Delete")
        time.sleep(0.2)
        return True

    def insert(self, text):
        self.cmd("Input.insertText", text=text)
        time.sleep(0.5)

    def press_enter(self):
        self.cmd("Input.dispatchKeyEvent", type="rawKeyDown", windowsVirtualKeyCode=13, code="Enter", key="Enter")
        self.cmd("Input.dispatchKeyEvent", type="char", text="\r")
        self.cmd("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=13, code="Enter", key="Enter")

    def send_by_click(self):
        return self.js("""
        (() => {
            const btns = [...document.querySelectorAll('button, [role="button"], [class*="send"]')];
            let b = btns.find(x => {
                const a = (x.getAttribute('aria-label')||'').trim();
                return a === '发送' || a === '发送消息' || a === 'Send message' || a === 'Send';
            });
            if (!b) b = document.querySelector('.chat-input-v2-send-button, .cr-send-button');
            if (!b) {
                b = btns.find(x => /send[-_]?button/i.test((x.className||'').toString()));
            }
            if (!b) return "no-btn";
            if (b.disabled) return "disabled";
            b.click();
            return "clicked:" + (b.getAttribute('aria-label') || (b.className||'').toString().slice(0,30));
        })()
        """)

    def left(self):
        return self.js("""
        (() => {
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return -1;
            return el.value !== undefined ? el.value.length : el.textContent.length;
        })()
        """)

    def send_text(self, text):
        if not self.focus_input():
            return "no-input"
        self.insert(text)
        time.sleep(0.5)
        # 先试点击
        r = self.send_by_click()
        time.sleep(1.5)
        l = self.left()
        if l == 0:
            return f"点击OK({r})"
        # 点击失败，试回车
        if r == "no-btn" or r == "disabled" or l > 0:
            self.focus_input()  # 重新聚焦
            self.insert(text)
            time.sleep(0.5)
            self.press_enter()
            time.sleep(1.5)
            l2 = self.left()
            if l2 == 0:
                return f"回车OK"
            return f"失败 btn={r} 剩余={l2}"
        return f"异常 btn={r} 剩余={l}"

def send(ai, text):
    if ai not in APPS: return f"❌ 未配置: {ai}"
    port, kw = APPS[ai]
    try:
        t = Tab(port, kw)
        r = t.send_text(text)
        return f"✅ {ai}: {r}"
    except Exception as e:
        return f"❌ {ai}: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python cdp_v4.py <AI名字> <文字>")
        print("可用:", list(APPS.keys()))
        sys.exit()
    print(send(sys.argv[1], sys.argv[2]))


