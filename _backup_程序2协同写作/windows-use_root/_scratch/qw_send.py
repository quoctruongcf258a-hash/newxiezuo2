import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9226/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
target = None
for p in pages:
    if "qianwen.com" in p.get("url",""): target = p; break
if not target: target = pages[0]

ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
mid = 0
def cmd(method, **params):
    global mid
    mid += 1
    ws.send(json.dumps({"id":mid,"method":method,"params":params}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid: return r
def js(code):
    return cmd("Runtime.evaluate", expression=code, returnByValue=True)["result"]["result"].get("value")

# 清空
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    el.textContent = ''; el.innerHTML = '';
})()
""")
time.sleep(0.3)

# 真实点击输入框 + insertText
box = js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    const r = el.getBoundingClientRect();
    return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
})()
""")
cmd("Input.dispatchMouseEvent", type="mousePressed", x=box["x"], y=box["y"], button="left", clickCount=1)
cmd("Input.dispatchMouseEvent", type="mouseReleased", x=box["x"], y=box["y"], button="left", clickCount=1)
time.sleep(0.3)
cmd("Input.insertText", text="【千问最终测】收到回千问 OK")
time.sleep(0.8)
print("写入后:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return (el.value !== undefined ? el.value : el.textContent).slice(0, 60);
})()
"""))

# 点 aria="发送消息"
print("发送:", js("""
(() => {
    const btns = [...document.querySelectorAll('button')];
    let b = btns.find(x => (x.getAttribute('aria-label')||'') === '发送消息');
    if (!b) b = btns.find(x => (x.getAttribute('aria-label')||'').includes('发送'));
    if (!b) return "没找到";
    if (b.disabled) return "disabled";
    b.click();
    return `已点击 aria="${b.getAttribute('aria-label')}"`;
})()
"""))
time.sleep(1.5)
print("剩余:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.value !== undefined ? el.value.length : el.textContent.length;
})()
"""))
