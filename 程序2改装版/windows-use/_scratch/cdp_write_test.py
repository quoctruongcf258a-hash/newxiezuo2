import json, urllib.request, sys
import websocket

def list_tabs(port=9222):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
        return json.load(f)

class Tab:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url)
        self.mid = 0
    def cmd(self, method, **params):
        self.mid += 1
        self.ws.send(json.dumps({"id": self.mid, "method": method, "params": params}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.mid:
                return r
    def js(self, code):
        r = self.cmd("Runtime.evaluate", expression=code, returnByValue=True, awaitPromise=False)
        return r.get("result", {}).get("result", {}).get("value")

tabs = [t for t in list_tabs() if t.get("type") == "page"]
print(f"标签页 {len(tabs)} 个")
for i, t in enumerate(tabs):
    print(f"  [{i}] {t.get('title','?')[:50]}  {t.get('url','?')[:60]}")

# 选第一个非 sign_in 的
target = None
for t in tabs:
    if "sign_in" not in t.get("url", ""):
        target = t; break
if target is None:
    print("❌ 没有已登录的标签页"); sys.exit(1)

print(f"\n目标: {target.get('title')}")
tab = Tab(target["webSocketDebuggerUrl"])

# 1. 读标题
print("标题:", tab.js("document.title"))

# 2. 找输入框
print("\n找输入框：")
input_info = tab.js("""
(() => {
    const cands = document.querySelectorAll('textarea, [contenteditable="true"], input[type="text"]');
    if (!cands.length) return "❌ 没找到";
    return [...cands].map((el, i) => 
        `[${i}] ${el.tagName} class="${el.className}" placeholder="${el.placeholder || ''}"`
    ).join("\\n");
})()
""")
print(input_info)

# 3. 找发送按钮
print("\n找发送按钮：")
btn_info = tab.js("""
(() => {
    const btns = [...document.querySelectorAll('button')].filter(b => 
        /send|发送|提交/i.test(b.getAttribute('aria-label') || b.textContent || '') ||
        b.type === 'submit'
    );
    if (!btns.length) return "❌ 没找到";
    return btns.map((b, i) => `[${i}] "${b.textContent.trim().slice(0,20)}" type=${b.type} disabled=${b.disabled}`).join("\\n");
})()
""")
print(btn_info)

# 4. 写内容（不发送）
print("\n写入测试内容：")
result = tab.js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return "❌ 没输入框";
    el.focus();
    if (el.tagName === 'TEXTAREA') {
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(el, '【CDP自动化测试】收到请回1');
        el.dispatchEvent(new Event('input', {bubbles: true}));
    } else {
        document.execCommand('insertText', false, '【CDP自动化测试】收到请回1');
    }
    return "✅ 已写入，检查页面是否显示文字";
})()
""")
print(result)
