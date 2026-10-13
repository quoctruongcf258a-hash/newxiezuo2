import json, urllib.request, websocket, time

# (名字, 端口, 页面URL关键词)
APPS = [
    ("CodeBuddy", 9223, ""),
    ("QUEST",     9224, ""),
    ("Doubao",    9225, ""),
    ("Qianwen",   9226, "qianwen.com"),   # 关键：选对页面
    ("WorkBuddy", 9227, ""),
    ("ZCode",     9228, ""),
]

class Tab:
    def __init__(self, port, url_kw=""):
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
            pages = [t for t in json.load(f) if t.get("type")=="page"]
        target = None
        if url_kw:
            for p in pages:
                if url_kw in p.get("url",""):
                    target = p; break
        if target is None:
            target = pages[0]
        self.ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
        self.mid = 0
        self.title = target.get("title", "")
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
                document.execCommand('insertText', false, {json.dumps(text)});
                el.dispatchEvent(new Event('input', {{bubbles:true}}));
            }}
            return "ok";
        }})()
        """)

    def enter(self):
        return self.js("""
        (() => {
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return "no-input";
            el.focus();
            const o = {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true, cancelable:true};
            el.dispatchEvent(new KeyboardEvent('keydown', o));
            el.dispatchEvent(new KeyboardEvent('keypress', o));
            el.dispatchEvent(new KeyboardEvent('keyup', o));
            return "ok";
        })()
        """)

    def find_btn(self):
        return self.js("""
        (() => {
            // 找所有 disabled=false 的 button / [role=button]
            const all = [...document.querySelectorAll('button, [role="button"], div[class*="send"], svg[class*="send"]')];
            const arr = all.filter(b => !b.disabled && b.getBoundingClientRect().width > 0);
            if (!arr.length) return "no";
            // 找靠近输入框的
            const inp = document.querySelector('textarea, [contenteditable="true"]');
            const ir = inp ? inp.getBoundingClientRect() : {x:0,y:0};
            arr.sort((a,b) => {
                const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
                const da = Math.hypot(ra.x-ir.x, ra.y-ir.y);
                const db = Math.hypot(rb.x-ir.x, rb.y-ir.y);
                return da - db;
            });
            return arr.slice(0,3).map((b,i) => {
                const r = b.getBoundingClientRect();
                return `[${i}] tag=${b.tagName} cls="${(b.className||'').toString().slice(0,40)}" pos=(${Math.round(r.x)},${Math.round(r.y)})`;
            }).join('\\n');
        })()
        """)

print(f"{'AI':12} {'页面':35} {'写入':6} {'回车':6}")
print("=" * 70)

for name, port, kw in APPS:
    try:
        t = Tab(port, kw)
        w = t.write(f"【CDP测试】{name} 收到请回OK")
        time.sleep(0.3)
        e = t.enter()
        print(f"{name:12} {t.title[:33]:35} {w:6} {e:6}")
    except Exception as ex:
        print(f"{name:12} ❌ {ex}")
