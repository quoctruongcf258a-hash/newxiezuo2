import json, urllib.request, websocket, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9226

with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
target = pages[0]
print(f"连接端口 {PORT}: {target.get('title')}")

ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
mid = 0
def js(code):
    global mid
    mid += 1
    ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r.get("result",{}).get("result",{}).get("value")

# 找输入框右侧的按钮
print("\n=== 输入框右侧的所有按钮/svg ===")
print(js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
    if (!el) return "no-input";
    const er = el.getBoundingClientRect();
    // 抓整个页面上的 button 和 svg，找在输入框右边+下方的
    const all = [...document.querySelectorAll('button, [role="button"], svg')];
    const near = all.filter(b => {
        const r = b.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return false;
        // 输入框下方 100 像素内，或右边
        return Math.abs(r.y - er.y) < 100 && r.x > er.x + er.width * 0.5;
    });
    return near.map((b,i) => {
        const r = b.getBoundingClientRect();
        const cls = (b.className||'').toString().slice(0,60);
        return `[${i}] ${b.tagName} cls="${cls}" pos=(${Math.round(r.x)},${Math.round(r.y)}) ${Math.round(r.width)}x${Math.round(r.height)}`;
    }).join('\\n');
})()
"""))
