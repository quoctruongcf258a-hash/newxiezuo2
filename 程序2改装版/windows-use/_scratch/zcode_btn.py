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

print("=== 输入框下方整片区域的所有元素 ===")
print(js("""
(() => {
    const inp = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
    if (!inp) return "no-input";
    const ir = inp.getBoundingClientRect();
    console.log = () => {};  // 静音
    // 抓页面上所有可见元素，过滤出在输入框附近的
    const all = [...document.querySelectorAll('*')];
    const near = all.filter(el => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return false;
        // 输入框下方 150 像素内
        return r.y > ir.y + ir.height - 10 && r.y < ir.y + ir.height + 150;
    });
    // 按 y 坐标排序
    near.sort((a,b) => a.getBoundingClientRect().y - b.getBoundingClientRect().y);
    return near.slice(0, 40).map((el, i) => {
        const r = el.getBoundingClientRect();
        const cls = (el.className||'').toString().slice(0, 60);
        const txt = (el.textContent||'').trim().slice(0, 20);
        return `[${i}] ${el.tagName} cls="${cls}" text="${txt}" pos=(${Math.round(r.x)},${Math.round(r.y)}) ${Math.round(r.width)}x${Math.round(r.height)}`;
    }).join('\\n');
})()
"""))
