import json, urllib.request, websocket

with urllib.request.urlopen("http://127.0.0.1:9225/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=15)
mid = 0
def js(code):
    global mid
    mid += 1
    ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r.get("result",{}).get("result",{}).get("value")

print("=== 输入框下 200px 内所有按钮 ===")
print(js("""
(() => {
    const inp = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
    if (!inp) return "no-input";
    const ir = inp.getBoundingClientRect();
    const btns = [...document.querySelectorAll('button, [role="button"]')].filter(b => {
        const r = b.getBoundingClientRect();
        if (r.width === 0) return false;
        return r.y > ir.y - 50 && r.y < ir.y + ir.height + 150;
    });
    btns.sort((a,b) => a.getBoundingClientRect().y - b.getBoundingClientRect().y);
    return btns.map((b, i) => {
        const r = b.getBoundingClientRect();
        const aria = b.getAttribute('aria-label') || '';
        const title = b.getAttribute('title') || '';
        const txt = (b.textContent||'').trim().slice(0, 20);
        const cls = (b.className||'').toString().slice(0, 50);
        return `[${i}] aria="${aria}" title="${title}" text="${txt}" cls="${cls}" pos=(${Math.round(r.x)},${Math.round(r.y)}) ${Math.round(r.width)}x${Math.round(r.height)}`;
    }).join('\\n');
})()
"""))
