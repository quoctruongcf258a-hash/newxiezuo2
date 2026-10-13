"""CDP 通用发送器 —— 多策略自适应"""
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
                el.textContent = ''; el.innerHTML = '';
                document.execCommand('insertText', false, {json.dumps(text)});
                el.dispatchEvent(new Event('input', {{bubbles:true}}));
            }}
            return "ok";
        }})()
        """)

    def send(self):
        return self.js("""
        (() => {
            const inp = document.querySelector('textarea, [contenteditable="true"]');
            if (!inp) return "no-input";
            const ir = inp.getBoundingClientRect();

            // 策略1：aria="发送"
            let b = [...document.querySelectorAll('button')].find(x =>
                (x.getAttribute('aria-label')||'') === '发送');
            if (b) { b.click(); return "aria发送"; }

            // 策略2：class 含 chat-input-v2-send-button / send-button
            b = document.querySelector('.chat-input-v2-send-button, [class*="chat-input-v2-send-button"]');
            if (b) { b.click(); return "chat-send-btn"; }

            // 策略3：class 含 send 的小元素
            b = [...document.querySelectorAll('[class*="send"]')].find(x => {
                const cls = (x.className||'').toString();
                return /send[-_]?button|sendbtn|send-btn/i.test(cls);
            });
            if (b) { b.click(); return "class-send"; }

            // 策略4：输入框右下最近的按钮
            const near = [...document.querySelectorAll('button, [role="button"]')].filter(x => {
                const r = x.getBoundingClientRect();
                return r.width > 0 && r.y > ir.y - 10 && r.y < ir.y + ir.height + 100 && r.x > ir.x + ir.width - 100;
            });
            if (near.length) {
                near.sort((a,b) => b.getBoundingClientRect().x - a.getBoundingClientRect().x);
                near[0].click();
                return "near";
            }

            // 策略5：回车
            inp.focus();
            const o = {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true, cancelable:true};
            inp.dispatchEvent(new KeyboardEvent('keydown', o));
            inp.dispatchEvent(new KeyboardEvent('keypress', o));
            inp.dispatchEvent(new KeyboardEvent('keyup', o));
            return "enter";
        })()
        """)

    def send_text(self, text):
        w = self.write(text)
        if w != "ok": return f"write={w}"
        time.sleep(0.5)
        s = self.send()
        time.sleep(1.2)
        left = self.js("""
        (() => {
            const el = document.querySelector('textarea, [contenteditable="true"]');
            return el.value !== undefined ? el.value.length : el.textContent.length;
        })()
        """)
        return f"send={s} 剩余={left}"


def send(ai_name, text):
    if ai_name not in APPS: return f"❌ 未配置: {ai_name}"
    port, kw = APPS[ai_name]
    try:
        t = Tab(port, kw)
        return f"✅ {ai_name} [{t.title[:30]}]: {t.send_text(text)}"
    except Exception as e:
        return f"❌ {ai_name}: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python cdp_send_all.py <AI名字> <文字>")
        print("可用:", list(APPS.keys()))
        sys.exit()
    print(send(sys.argv[1], sys.argv[2]))
