import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9228/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
t = pages[0]
print("页面:", t.get("title"))
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=15)
mid = 0
def js(code):
    global mid
    mid += 1
    ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r.get("result",{}).get("result",{}).get("value")

# 1. 找输入框并写入
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
    el.focus();
    if (el.tagName === 'TEXTAREA') {
        const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        s.call(el, '【ZCode单测】收到请回ZCode OK');
        el.dispatchEvent(new Event('input', {bubbles:true}));
    } else {
        el.textContent = '';
        document.execCommand('insertText', false, '【ZCode单测】收到请回ZCode OK');
    }
})()
""")
time.sleep(0.5)

# 2. 找到输入框容器，列出所有可点元素
print("\n=== 输入框附近的元素 ===")
print(js("""
(() => {
    const inp = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
    const ir = inp.getBoundingClientRect();
    const all = [...document.querySelectorAll('*')];
    const near = all.filter(el => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return false;
        // 在输入框的右下方 200x100 区域
        return r.y > ir.y - 10 && r.y < ir.y + 80 && r.x > ir.x + ir.width - 100 && r.x < ir.x + ir.width + 200;
    });
    return near.slice(0, 30).map((el, i) => {
        const r = el.getBoundingClientRect();
        const cls = (el.className||'').toString().slice(0, 50);
        return `[${i}] ${el.tagName} class="${cls}" pos=(${Math.round(r.x)},${Math.round(r.y)}) ${Math.round(r.width)}x${Math.round(r.height)}`;
    }).join('\\n');
})()
"""))
