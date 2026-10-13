import json, urllib.request
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
print("目标:", target.get("title"))

# 1. 找输入框附近的按钮（父节点附近 5 层内的所有 button）
r = tab.js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return "no-input";
    let node = el;
    let found = new Set();
    for (let i=0; i<6 && node; i++) {
        node.querySelectorAll('button, [role="button"], div[class*="send"], div[class*="submit"]').forEach(b => found.add(b));
        node = node.parentElement;
    }
    return [...found].map((b, i) => {
        const r = b.getBoundingClientRect();
        const cls = (b.className || '').toString().slice(0,60);
        const txt = (b.textContent || '').trim().slice(0,20);
        const aria = b.getAttribute('aria-label') || '';
        const dis = b.disabled;
        return `[${i}] tag=${b.tagName} disabled=${dis} aria="${aria}" text="${txt}" class="${cls}" pos=(${Math.round(r.x)},${Math.round(r.y)}) size=${Math.round(r.width)}x${Math.round(r.height)}`;
    }).join("\\n");
})()
""")
print("\n=== 输入框附近按钮 ===")
print(r)

# 2. 看 svg 图标
r2 = tab.js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return "no-input";
    let node = el;
    for (let i=0; i<6 && node; i++) {
        const svgs = node.querySelectorAll('svg');
        if (svgs.length) {
            return [...svgs].map((s, i) => {
                const parent = s.parentElement;
                const ptag = parent.tagName;
                const pcls = (parent.className || '').toString().slice(0,60);
                const r = s.getBoundingClientRect();
                return `[${i}] svg parent=${ptag} class="${pcls}" pos=(${Math.round(r.x)},${Math.round(r.y)})`;
            }).join("\\n");
        }
        node = node.parentElement;
    }
    return "没找到 svg";
})()
""")
print("\n=== 输入框附近 svg 图标 ===")
print(r2)
