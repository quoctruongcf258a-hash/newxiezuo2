import json, urllib.request, websocket

with urllib.request.urlopen("http://127.0.0.1:9224/json", timeout=5) as f:
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

print("=== 输入框附近所有元素（下方150px内） ===")
print(js("""
(() => {
    const inp = document.querySelector('textarea, [contenteditable="true"]');
    if (!inp) return "no-input";
    const ir = inp.getBoundingClientRect();
    const all = [...document.querySelectorAll('*')].filter(el => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.width > 200) return false;
        return r.y >= ir.y - 20 && r.y <= ir.y + ir.height + 150;
    });
    all.sort((a,b) => b.getBoundingClientRect().x - a.getBoundingClientRect().x);
    return all.slice(0, 30).map((el, i) => {
        const r = el.getBoundingClientRect();
        const cls = (el.className||'').toString().slice(0, 70);
        const aria = el.getAttribute('aria-label') || '';
        const title = el.getAttribute('title') || '';
        const txt = (el.textContent||'').trim().slice(0, 20);
        return `[${i}] ${el.tagName} aria="${aria}" title="${title}" text="${txt}" cls="${cls}" pos=(${Math.round(r.x)},${Math.round(r.y)}) ${Math.round(r.width)}x${Math.round(r.height)}`;
    }).join('\\n');
})()
"""))
