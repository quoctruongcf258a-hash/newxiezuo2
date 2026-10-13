import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9226/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
target = None
for p in pages:
    if "qianwen.com" in p.get("url",""): target = p; break
if not target: target = pages[0]
print("页面:", target.get("title"))

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

# 刷新清状态
cmd("Page.enable")
cmd("Page.reload", ignoreCache=True)
time.sleep(10)

# 点输入框
box = js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
})()
""")
if not box: print("无输入框"); exit()
print("输入框:", box)
cmd("Input.dispatchMouseEvent", type="mousePressed", x=box["x"], y=box["y"], button="left", clickCount=1)
cmd("Input.dispatchMouseEvent", type="mouseReleased", x=box["x"], y=box["y"], button="left", clickCount=1)
time.sleep(0.4)

# 写入
cmd("Input.insertText", text="【千问鼠标测】收到回OK")
time.sleep(1)
print("写入后:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return (el.value !== undefined ? el.value : el.textContent).slice(0, 60);
})()
"""))

# 找发送按钮的坐标
btn = js("""
(() => {
    const b = [...document.querySelectorAll('button')].find(x => (x.getAttribute('aria-label')||'').includes('发送'));
    if (!b) return null;
    const r = b.getBoundingClientRect();
    return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2), aria: b.getAttribute('aria-label')};
})()
""")
if not btn:
    print("找不到发送按钮"); exit()
print("发送按钮:", btn)

# CDP 真鼠标点击（mousePressed + mouseReleased）
cmd("Input.dispatchMouseEvent", type="mouseMoved", x=btn["x"], y=btn["y"])
time.sleep(0.1)
cmd("Input.dispatchMouseEvent", type="mousePressed", x=btn["x"], y=btn["y"], button="left", clickCount=1)
time.sleep(0.08)
cmd("Input.dispatchMouseEvent", type="mouseReleased", x=btn["x"], y=btn["y"], button="left", clickCount=1)
print("已用真鼠标点击")
time.sleep(2)

left = js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.value !== undefined ? el.value.length : el.textContent.length;
})()
""")
print("剩余字符:", left)

# 看有没有新消息
msgs = js("""
(() => {
    const sels = ['[class*="message"]', '[class*="chat"]', '[role="log"]'];
    let n = 0;
    for (const s of sels) { n += document.querySelectorAll(s).length; }
    return n;
})()
""")
print("消息块数量:", msgs)
