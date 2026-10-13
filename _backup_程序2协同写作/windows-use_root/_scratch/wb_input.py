import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9227/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=15)
mid = 0
def cmd(method, **params):
    global mid
    mid += 1
    ws.send(json.dumps({"id":mid,"method":method,"params":params}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r

# 1. 先聚焦输入框（用 CDP 真实点击）
box = cmd("Runtime.evaluate", expression="""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {x: r.x + r.width/2, y: r.y + r.height/2};
})()
""", returnByValue=True)["result"]["result"]["value"]

if not box:
    print("找不到输入框"); exit()

print(f"点击位置: ({box['x']}, {box['y']})")
cmd("Input.dispatchMouseEvent", type="mousePressed", x=int(box["x"]), y=int(box["y"]), button="left", clickCount=1)
cmd("Input.dispatchMouseEvent", type="mouseReleased", x=int(box["x"]), y=int(box["y"]), button="left", clickCount=1)
time.sleep(0.5)

# 2. 用 CDP Input.insertText 真输入
MSG = "【WB真输入测】收到回WB OK"
cmd("Input.insertText", text=MSG)
time.sleep(0.8)

# 3. 检查按钮状态
btn = cmd("Runtime.evaluate", expression="""
(() => {
    const b = document.querySelector('.cr-send-button');
    if (!b) return "no-btn";
    return `disabled=${b.disabled} aria-disabled=${b.getAttribute('aria-disabled')}`;
})()
""", returnByValue=True)["result"]["result"]["value"]
print("按钮状态:", btn)

# 4. 点发送
r = cmd("Runtime.evaluate", expression="""
(() => {
    const b = document.querySelector('.cr-send-button');
    if (!b) return "no";
    if (b.disabled) return "still-disabled";
    b.click();
    return "clicked";
})()
""", returnByValue=True)["result"]["result"]["value"]
print("发送:", r)
time.sleep(1.2)

# 5. 看输入框是否清空
left = cmd("Runtime.evaluate", expression="""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.textContent.length;
})()
""", returnByValue=True)["result"]["result"]["value"]
print("剩余字符:", left)
