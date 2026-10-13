import json, urllib.request, time
import websocket

class CDP:
    def __init__(self, port=9222):
        self.port = port
    def list_tabs(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json", timeout=5) as f:
            return [t for t in json.load(f) if t.get("type") == "page"]
    def find_tab(self, keyword=""):
        for t in self.list_tabs():
            if keyword.lower() in (t.get("url","") + t.get("title","")).lower():
                return Tab(t["webSocketDebuggerUrl"])
        return None

class Tab:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=15)
        self.mid = 0
    def cmd(self, method, **params):
        self.mid += 1
        self.ws.send(json.dumps({"id": self.mid, "method": method, "params": params}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.mid: return r
    def js(self, code):
        r = self.cmd("Runtime.evaluate", expression=code, returnByValue=True)
        res = r.get("result", {}).get("result", {})
        if "exceptionDetails" in r.get("result", {}):
            return f"JS_ERROR: {r['result']['exceptionDetails']}"
        return res.get("value")

    def write(self, text):
        return self.js(f"""
        (() => {{
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return "找不到输入框";
            el.focus();
            if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {{
                const s = Object.getOwnPropertyDescriptor(
                    el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype, 'value').set;
                s.call(el, {json.dumps(text)});
                el.dispatchEvent(new Event('input', {{bubbles: true}}));
            }} else {{
                document.execCommand('insertText', false, {json.dumps(text)});
            }}
            return "已写入";
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
                node.querySelectorAll('.ds-button--primary, .ds-button--filled, button[type="submit"], [aria-label*="send"], [aria-label*="发送"]').forEach(b => found.add(b));
                node = node.parentElement;
            }
            const arr = [...found];
            if (arr.length) {
                arr.sort((a,b) => b.getBoundingClientRect().y - a.getBoundingClientRect().y);
                arr[0].click();
                return "已发送";
            }
            return "未找到按钮";
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
        last = ""; last_change = time.time(); start = time.time()
        while time.time() - start < max_wait:
            cur = self.read_last()
            if cur != last:
                last = cur; last_change = time.time()
            elif time.time() - last_change > seconds and cur:
                return cur
            time.sleep(1)
        return last


if __name__ == "__main__":
    cdp = CDP()
    tab = cdp.find_tab("deepseek")
    if not tab:
        print("没找到 DeepSeek"); exit()
    print("已连 DeepSeek")
    print("写入:", tab.write("【Adapter测试】1+1=?"))
    time.sleep(0.5)
    print("发送:", tab.send())
    print("等回复...")
    reply = tab.wait_stable(seconds=3, max_wait=60)
    print("\n=== 回复 ===")
    print(reply[:800])
