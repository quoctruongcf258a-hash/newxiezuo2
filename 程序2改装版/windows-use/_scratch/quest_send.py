import json, urllib.request, websocket, time

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

# 清空 + 写入
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    el.textContent = ''; el.innerHTML = '';
})()
""")
time.sleep(0.3)
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    document.execCommand('insertText', false, '【QUEST最终测】收到回QUEST OK');
})()
""")
time.sleep(0.5)
print("写入后:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.textContent.slice(0, 60);
})()
"""))

# 点 aria="Send message" 或 aria 含 send
print("发送:", js("""
(() => {
    const btns = [...document.querySelectorAll('button')];
    let b = btns.find(x => {
        const a = (x.getAttribute('aria-label')||'').toLowerCase();
        return a === 'send message' || a === 'send' || a === '发送';
    });
    if (!b) return "没找到";
    b.click();
    return `已点击 aria="${b.getAttribute('aria-label')}"`;
})()
"""))
time.sleep(1.2)
print("剩余:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.textContent.length;
})()
"""))
