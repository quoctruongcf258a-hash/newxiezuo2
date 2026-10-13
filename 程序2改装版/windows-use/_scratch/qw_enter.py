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

# 1. 刷新页面（清掉卡住的转圈）
cmd("Page.enable")
cmd("Page.reload", ignoreCache=True)
time.sleep(8)

# 2. 重新找输入框 + 真点击
box = js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
})()
""")
if not box:
    print("找不到输入框"); exit()
print("输入框位置:", box)

cmd("Input.dispatchMouseEvent", type="mousePressed", x=box["x"], y=box["y"], button="left", clickCount=1)
cmd("Input.dispatchMouseEvent", type="mouseReleased", x=box["x"], y=box["y"], button="left", clickCount=1)
time.sleep(0.5)

# 3. 真输入
cmd("Input.insertText", text="【千问测】1+1=?")
time.sleep(1)
print("写入后:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return (el.value !== undefined ? el.value : el.textContent).slice(0, 60);
})()
"""))

# 4. 真回车（CDP 键盘事件）—— rawKeyDown + char + keyUp
print("按真回车：")
cmd("Input.dispatchKeyEvent", type="rawKeyDown", windowsVirtualKeyCode=13, code="Enter", key="Enter", modifiers=0)
time.sleep(0.05)
cmd("Input.dispatchKeyEvent", type="char", text="\r", unmodifiedText="\r")
time.sleep(0.05)
cmd("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=13, code="Enter", key="Enter", modifiers=0)
time.sleep(2)

print("剩余字符:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.value !== undefined ? el.value.length : el.textContent.length;
})()
"""))
