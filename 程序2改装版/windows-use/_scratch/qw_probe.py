import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9226/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
# 选 qianwen.com 的页面
target = None
for p in pages:
    if "qianwen.com" in p.get("url",""):
        target = p; break
if not target: target = pages[0]
print("页面:", target.get("title"), target.get("url")[:60])

ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
mid = 0
def cmd(method, **params):
    global mid
    mid += 1
    ws.send(json.dumps({"id":mid,"method":method,"params":params}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r

def js(code):
    return cmd("Runtime.evaluate", expression=code, returnByValue=True)["result"]["result"].get("value")

# 1. 找输入框位置
box = js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
})()
""")
print("输入框位置:", box)
if not box: exit()

# 2. 真实鼠标点击
cmd("Input.dispatchMouseEvent", type="mousePressed", x=box["x"], y=box["y"], button="left", clickCount=1)
cmd("Input.dispatchMouseEvent", type="mouseReleased", x=box["x"], y=box["y"], button="left", clickCount=1)
time.sleep(0.5)

# 3. 真输入
cmd("Input.insertText", text="【千问真输入测】收到回千问 OK")
time.sleep(0.8)
print("写入后:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return (el.value !== undefined ? el.value : el.textContent).slice(0, 60);
})()
"""))

# 4. 看输入框右下角有哪些按钮
print("\n=== 输入框附近按钮 ===")
print(js("""
(() => {
    const inp = document.querySelector('textarea, [contenteditable="true"]');
    const ir = inp.getBoundingClientRect();
    const all = [...document.querySelectorAll('button, [class*="send"]')].filter(el => {
        const r = el.getBoundingClientRect();
        if (r.width === 0) return false;
        return r.y >= ir.y - 20 && r.y <= ir.y + ir.height + 80;
    });
    all.sort((a,b) => b.getBoundingClientRect().x - a.getBoundingClientRect().x);
    return all.slice(0, 15).map((el, i) => {
        const r = el.getBoundingClientRect();
        const cls = (el.className||'').toString().slice(0, 60);
        const aria = el.getAttribute('aria-label') || '';
        return `[${i}] ${el.tagName} aria="${aria}" cls="${cls}" pos=(${Math.round(r.x)},${Math.round(r.y)}) ${Math.round(r.width)}x${Math.round(r.height)}`;
    }).join('\\n');
})()
"""))
