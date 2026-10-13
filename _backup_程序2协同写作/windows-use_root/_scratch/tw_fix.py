import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9225/json", timeout=5) as f:
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

# 清空
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    el.textContent = ''; el.innerHTML = '';
})()
""")
time.sleep(0.3)

# 写入
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    document.execCommand('insertText', false, '【TW最终测】TraeWork收到请回TW OK');
})()
""")
time.sleep(0.5)

# 看输入框内容
print("写入后:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.textContent;
})()
"""))

# 找 chat-input-v2-send-button 并点击
print("点击结果:", js("""
(() => {
    const btn = document.querySelector('.chat-input-v2-send-button');
    if (!btn) return "找不到";
    const r = btn.getBoundingClientRect();
    const info = `class="${(btn.className||'').toString()}" pos=(${Math.round(r.x)},${Math.round(r.y)}) ${Math.round(r.width)}x${Math.round(r.height)} disabled=${btn.disabled}`;
    btn.click();
    return "已点击: " + info;
})()
"""))
time.sleep(1.5)
print("剩余字符:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.textContent.length;
})()
"""))
