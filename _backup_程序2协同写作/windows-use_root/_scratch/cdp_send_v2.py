"""CDP 发送器 v2 —— 支持：写入 + 优先点 aria=发送 按钮，兜底回车"""
import json, urllib.request, websocket, time, sys

APPS = {
    "CodeBuddy": (9223, ""),
    "QUEST":     (9224, ""),
    "Doubao":    (9225, ""),
    "Qianwen":   (9226, "qianwen.com"),
    "WorkBuddy": (9227, ""),
    "ZCode":     (9228, ""),
    "DeepSeek":  (9222, "deepseek"),
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
    def js(self, code):
        self.mid += 1
        self.ws.send(json.dumps({"id":self.mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.mid:
                return r.get("result",{}).get("result",{}).get("value")

    def write(self, text):
        # 先清空再写
        return self.js(f"""
        (() => {{
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return "no-input";
            el.focus();
            if (el.tagName === 'TEXTAREA') {{
                const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
                s.call(el, {json.dumps(text)});
                el.dispatchEvent(new Event('input', {{bubbles:true}}));
            }} else {{
                el.textContent = '';
                el.innerHTML = '';
                document.execCommand('insertText', false, {json.dumps(text)});
            }}
            return "ok";
        }})()
        """)

    def send(self):
        # 1. 优先点 aria="发送" 按钮
        r = self.js("""
        (() => {
            const btns = [...document.querySelectorAll('button, [role="button"]')];
            const sendBtn = btns.find(b => {
                const a = (b.getAttribute('aria-label') || '').toLowerCase();
                const t = (b.textContent || '').trim();
                return a === '发送' || a === 'send' || t === '发送' || t === 'Send';
            });
            if (sendBtn) {
                sendBtn.click();
                return "clicked-aria";
            }
            // 2. 兜底：找输入框附近的唯一按钮（含 svg 向上的箭头）
            const inp = document.querySelector('textarea, [contenteditable="true"]');
            if (!inp) return "no-input";
            const ir = inp.getBoundingClientRect();
            const cands = [...document.querySelectorAll('button')].filter(b => {
                const r = b.getBoundingClientRect();
                return r.width > 0 && r.y > ir.y - 10 && r.y < ir.y + ir.height + 100 && r.x > ir.x + ir.width - 100;
            });
            if (cands.length) {
                cands[cands.length-1].click();
                return "clicked-near";
            }
            // 3. 兜底：回车
            const o = {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true, cancelable:true};
            inp.focus();
            inp.dispatchEvent(new KeyboardEvent('keydown', o));
            inp.dispatchEvent(new KeyboardEvent('keypress', o));
            inp.dispatchEvent(new KeyboardEvent('keyup', o));
            return "enter";
        })()
        """)
        return r

    def send_text(self, text):
        w = self.write(text)
        if w != "ok":
            return f"write={w}"
        time.sleep(0.5)
        s = self.send()
        time.sleep(1)
        # 检查是否清空
        left = self.js("""
        (() => {
            const el = document.querySelector('textarea, [contenteditable="true"]');
            return el.value !== undefined ? el.value.length : el.textContent.length;
        })()
        """)
        return f"write=ok send={s} 剩余字符={left}"


def send(ai_name, text):
    if ai_name not in APPS:
        return f"❌ 未配置: {ai_name}"
    port, kw = APPS[ai_name]
    try:
        t = Tab(port, kw)
        result = t.send_text(text)
        return f"✅ {ai_name}: {result}"
    except Exception as e:
        return f"❌ {ai_name}: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python cdp_send_v2.py <AI名字> <文字>")
        print("可用:", list(APPS.keys()))
        sys.exit()
    print(send(sys.argv[1], sys.argv[2]))
