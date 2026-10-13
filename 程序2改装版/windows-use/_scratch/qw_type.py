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

# 1. 点输入框
box = js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
})()
""")
if not box: print("找不到输入框"); exit()
print("输入框:", box)
cmd("Input.dispatchMouseEvent", type="mousePressed", x=box["x"], y=box["y"], button="left", clickCount=1)
cmd("Input.dispatchMouseEvent", type="mouseReleased", x=box["x"], y=box["y"], button="left", clickCount=1)
time.sleep(0.5)

# 2. Ctrl+A 清空 + Delete
cmd("Input.dispatchKeyEvent", type="rawKeyDown", windowsVirtualKeyCode=65, code="KeyA", key="a", modifiers=2)
cmd("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=65, code="KeyA", key="a", modifiers=2)
time.sleep(0.15)
cmd("Input.dispatchKeyEvent", type="rawKeyDown", windowsVirtualKeyCode=46, code="Delete", key="Delete")
cmd("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=46, code="Delete", key="Delete")
time.sleep(0.3)

# 3. 逐字符输入（真键盘模拟，每字符 80ms）
msg = "test hello"
print(f"逐字符输入：{msg}")
for ch in msg:
    # 用 Input.insertText 单独每个字符（比 dispatchKeyEvent 稳，含中英文）
    cmd("Input.insertText", text=ch)
    time.sleep(0.08)

time.sleep(0.8)
print("输入框内容:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return (el.value !== undefined ? el.value : el.textContent).slice(0, 80);
})()
"""))

# 4. 检查按钮状态
print("发送按钮:", js("""
(() => {
    const b = [...document.querySelectorAll('button')].find(x => (x.getAttribute('aria-label')||'').includes('发送'));
    if (!b) return "无按钮";
    return `aria="${b.getAttribute('aria-label')}" disabled=${b.disabled}`;
})()
"""))

# 5. 用 CDP 真鼠标点发送
btn = js("""
(() => {
    const b = [...document.querySelectorAll('button')].find(x => (x.getAttribute('aria-label')||'').includes('发送'));
    if (!b) return null;
    const r = b.getBoundingClientRect();
    return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
})()
""")
if btn:
    print(f"点按钮 {btn}")
    cmd("Input.dispatchMouseEvent", type="mouseMoved", x=btn["x"], y=btn["y"])
    time.sleep(0.15)
    cmd("Input.dispatchMouseEvent", type="mousePressed", x=btn["x"], y=btn["y"], button="left", clickCount=1)
    time.sleep(0.1)
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=btn["x"], y=btn["y"], button="left", clickCount=1)
    print("已点击")
    time.sleep(2.5)
    print("剩余:", js("""
    (() => {
        const el = document.querySelector('textarea, [contenteditable="true"]');
        return el.value !== undefined ? el.value.length : el.textContent.length;
    })()
    """))
