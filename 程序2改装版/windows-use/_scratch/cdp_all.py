import json, urllib.request, time
import websocket

APPS = {
    "CodeBuddy": 9223,
    "QUEST":     9224,
    "Doubao":    9225,
    "Qianwen":   9226,
    "WorkBuddy": 9227,
    "ZCode":     9228,
    "DeepSeek":  9222,
    "Kimi":      9222,
}

class Tab:
    def __init__(self, port, keyword=""):
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
            tabs = [t for t in json.load(f) if t.get("type")=="page"]
        if not tabs:
            raise Exception(f"端口 {port} 没有页面")
        target = None
        if keyword:
            for t in tabs:
                if keyword.lower() in (t.get("url","") + t.get("title","")).lower():
                    target = t; break
        if target is None:
            target = tabs[0]
        self.ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
        self.mid = 0
        self.title = target.get("title", "")
        self.url = target.get("url", "")

    def cmd(self, method, **params):
        self.mid += 1
        self.ws.send(json.dumps({"id": self.mid, "method": method, "params": params}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.mid: return r

    def js(self, code):
        r = self.cmd("Runtime.evaluate", expression=code, returnByValue=True)
        res = r.get("result", {}).get("result", {})
        return res.get("value")

    def write(self, text):
        return self.js(f"""
        (() => {{
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return "no-input";
            el.focus();
            if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {{
                const s = Object.getOwnPropertyDescriptor(
                    el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype, 'value').set;
                s.call(el, {json.dumps(text)});
                el.dispatchEvent(new Event('input', {{bubbles: true}}));
            }} else {{
                document.execCommand('insertText', false, {json.dumps(text)});
            }}
            return "ok";
        }})()
        """)

    def send(self):
        return self.js("""
        (() => {
            const el = document.querySelector('textarea, [contenteditable="true"]');
            if (el) {
                const o = {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true, cancelable:true};
                el.dispatchEvent(new KeyboardEvent('keydown', o));
                el.dispatchEvent(new KeyboardEvent('keypress', o));
                el.dispatchEvent(new KeyboardEvent('keyup', o));
            }
            let node = el, found = new Set();
            for (let i=0; i<6 && node; i++) {
                node.querySelectorAll('button[type="submit"], [aria-label*="send"], [aria-label*="发送"], .ds-button--primary').forEach(b => found.add(b));
                node = node.parentElement;
            }
            const arr = [...found].filter(b => !b.disabled);
            if (arr.length) {
                arr.sort((a,b) => b.getBoundingClientRect().y - a.getBoundingClientRect().y);
                arr[0].click();
                return "clicked";
            }
            return "no-button";
        })()
        """)

    def read_last(self):
        return self.js("""
        (() => {
            const sels = [
                '[class*="assistant"][class*="message"]',
                '[class*="message"][class*="assistant"]',
                '[class*="assistant-message"]',
                '[data-role="assistant"]',
                '[class*="bot-message"]',
                '[class*="markdown-body"]',
                '[class*="markdown"]',
            ];
            for (const s of sels) {
                const els = document.querySelectorAll(s);
                if (els.length) return els[els.length-1].innerText;
            }
            const all = [...document.querySelectorAll('div, p')].filter(el => {
                const t = el.innerText || '';
                return t.length > 30 && el.children.length < 5;
            });
            return all.length ? all[all.length-1].innerText : "";
        })()
        """)

    def wait_stable(self, seconds=3, max_wait=180):
        last=""; t0=time.time(); tc=time.time()
        while time.time() - t0 < max_wait:
            cur = self.read_last()
            if cur != last:
                last = cur; tc = time.time()
            elif time.time() - tc > seconds and cur:
                return cur
            time.sleep(1)
        return last


def open_app(name, keyword=""):
    """按名字打开一个 AI 的标签页"""
    port = APPS.get(name)
    if not port:
        raise Exception(f"未配置: {name}")
    return Tab(port, keyword)


if __name__ == "__main__":
    # 演示：遍历所有 7 个 AI，读它们的标题
    for name in APPS:
        if name in ("Kimi",): continue
        try:
            t = Tab(APPS[name])
            print(f"✅ {name:12} port {APPS[name]}  title=[{t.title[:40]}]")
        except Exception as e:
            print(f"❌ {name:12} port {APPS[name]}  {e}")
