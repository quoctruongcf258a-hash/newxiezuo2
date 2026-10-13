import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9228/json", timeout=5) as f:
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

# 1. 清空输入框
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    el.textContent = '';
    el.innerHTML = '';
})()
""")
time.sleep(0.3)

# 2. 写入
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    document.execCommand('insertText', false, '【ZCode发送测】收到请回ZCode OK');
})()
""")
time.sleep(0.5)

# 3. 找 aria="发送" 的按钮并点击
r = js("""
(() => {
    const btns = [...document.querySelectorAll('button')];
    const sendBtn = btns.find(b => b.getAttribute('aria-label') === '发送');
    if (!sendBtn) return "找不到发送按钮";
    const disabled = sendBtn.disabled;
    sendBtn.click();
    return `已点击 (disabled=${disabled})`;
})()
""")
print("点发送:", r)
time.sleep(1)

# 4. 看输入框是否清空
left = js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.textContent.length;
})()
""")
print("输入框剩余字符:", left)
