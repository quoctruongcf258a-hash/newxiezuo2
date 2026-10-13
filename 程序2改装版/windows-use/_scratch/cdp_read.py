import json, urllib.request, time
import websocket

def list_tabs(port=9222):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
        return json.load(f)

class Tab:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url); self.mid = 0
    def cmd(self, method, **params):
        self.mid += 1
        self.ws.send(json.dumps({"id": self.mid, "method": method, "params": params}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.mid: return r
    def js(self, code):
        r = self.cmd("Runtime.evaluate", expression=code, returnByValue=True)
        return r.get("result", {}).get("result", {}).get("value")

tabs = [t for t in list_tabs() if t.get("type")=="page"]
target = [t for t in tabs if "sign_in" not in t.get("url","")][0]
tab = Tab(target["webSocketDebuggerUrl"])

# 找所有可能的"消息容器"
r = tab.js("""
(() => {
    const sels = [
        '[class*="message"]',
        '[class*="chat"] > div',
        '[class*="markdown"]',
        '[class*="assistant"]',
        '[class*="user"]',
        'main > div > div',
    ];
    let report = [];
    for (const s of sels) {
        const els = document.querySelectorAll(s);
        if (els.length > 0 && els.length < 200) {
            report.push(`${s} → ${els.length} 个`);
        }
    }
    return report.join("\\n");
})()
""")
print("=== 候选容器 ===")
print(r)

# 抓最后几段文字
r2 = tab.js("""
(() => {
    // 抓页面里所有文本 > 20 字的块
    const all = [...document.querySelectorAll('div, p')];
    const candidates = all.filter(el => {
        const t = el.innerText || '';
        return t.length > 20 && t.length < 5000 && el.children.length < 10;
    });
    // 去重、取最后 5 个
    const uniq = [];
    const seen = new Set();
    for (let i = candidates.length - 1; i >= 0 && uniq.length < 5; i--) {
        const t = candidates[i].innerText.trim();
        if (!seen.has(t)) { seen.add(t); uniq.push(t.slice(0, 300)); }
    }
    return uniq.join("\\n\\n---\\n\\n");
})()
""")
print("\n=== 最后几段文字 ===")
print(r2)
