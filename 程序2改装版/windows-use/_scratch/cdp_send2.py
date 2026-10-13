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
print("目标:", target.get("title"))

MSG = "【CDP测试2】收到请回数字 2"

# 1. 写内容
r = tab.js(f"""
(() => {{
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    if (el.tagName === 'TEXTAREA') {{
        const s = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        s.call(el, {json.dumps(MSG)});
        el.dispatchEvent(new Event('input', {{bubbles: true}}));
    }} else {{
        document.execCommand('insertText', false, {json.dumps(MSG)});
    }}
    return "写入完成";
}})()
""")
print("写:", r)
time.sleep(0.5)

# 2. 点发送按钮（找 ds-button--primary 且位置在输入框附近）
r2 = tab.js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    let node = el, found = new Set();
    for (let i=0; i<6 && node; i++) {
        node.querySelectorAll('.ds-button--primary, .ds-button--filled').forEach(b => found.add(b));
        node = node.parentElement;
    }
    const arr = [...found];
    if (!arr.length) return "❌ 没找到发送按钮";
    // 挑位置最靠下的（最接近输入框）
    arr.sort((a,b) => b.getBoundingClientRect().y - a.getBoundingClientRect().y);
    const btn = arr[0];
    const r = btn.getBoundingClientRect();
    btn.click();
    return `✅ 已点 (${Math.round(r.x)},${Math.round(r.y)}) class="${btn.className.slice(0,60)}"`;
})()
""")
print("点:", r2)
time.sleep(2)

# 3. 检查输入框是否清空
r3 = tab.js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (el.tagName === 'TEXTAREA') return el.value.length === 0 ? "✅ 已发送" : "⚠ 还在: " + el.value.slice(0,60);
    return el.textContent.length === 0 ? "✅ 已发送" : "⚠ 还在: " + el.textContent.slice(0,60);
})()
""")
print("结果:", r3)
