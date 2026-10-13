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

# 1. 清空
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    el.textContent = ''; el.innerHTML = '';
})()
""")
time.sleep(0.3)

# 2. 写入
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    document.execCommand('insertText', false, '【TW测】收到请回TW OK');
})()
""")
time.sleep(0.5)
print("写入完成，当前输入框:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.textContent.slice(0, 60);
})()
"""))

# 3. 精确点 class 含 chat-input-v2-send-button 的元素
print("发送:", js("""
(() => {
    const btn = document.querySelector('.chat-input-v2-send-button, [class*="chat-input-v2-send-button"]');
    if (!btn) return "找不到 send-button";
    const disabled = btn.disabled;
    btn.click();
    return `已点击 disabled=${disabled} class="${(btn.className||'').toString().slice(0,50)}"`;
})()
"""))
time.sleep(1.2)
print("剩余:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.textContent.length;
})()
"""))
