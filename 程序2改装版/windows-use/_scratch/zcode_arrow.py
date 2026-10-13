import json, urllib.request, websocket

with urllib.request.urlopen("http://127.0.0.1:9228/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
t = pages[0]
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

print("=== 输入框下 200px 内的所有按钮/可点元素 ===")
print(js("""
(() => {
    const inp = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
    if (!inp) return "no-input";
    const ir = inp.getBoundingClientRect();
    const all = [...document.querySelectorAll('button, [role="button"], svg, [class*="btn"], [class*="icon"], [class*="send"], [class*="submit"], [class*="arrow"], [class*="up"]')];
    const near = all.filter(el => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return false;
        return r.y > ir.y - 50 && r.y < ir.y + ir.height + 200;
    });
    near.sort((a,b) => a.getBoundingClientRect().y - b.getBoundingClientRect().y);
    return near.slice(0, 40).map((el, i) => {
        const r = el.getBoundingClientRect();
        const cls = (el.className||'').toString().slice(0, 70);
        const tag = el.tagName;
        const role = el.getAttribute('role') || '';
        const aria = el.getAttribute('aria-label') || '';
        return `[${i}] ${tag} role="${role}" aria="${aria}" class="${cls}" pos=(${Math.round(r.x)},${Math.round(r.y)}) ${Math.round(r.width)}x${Math.round(r.height)}`;
    }).join('\\n');
})()
"""))
