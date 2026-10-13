import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9226/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
target = pages[0]
print("连接:", target.get("title"), "|", target.get("url")[:80])

ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
mid = 0
def js(code):
    global mid
    mid += 1
    ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r.get("result",{}).get("result",{}).get("value")

# 1. 检查输入框类型 + 当前内容
info = js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
    if (!el) return "no-input";
    const r = el.getBoundingClientRect();
    return `tag=${el.tagName} cls="${(el.className||'').toString().slice(0,50)}" value="${(el.value !== undefined ? el.value : el.innerText || '').slice(0,50)}" pos=(${Math.round(r.x)},${Math.round(r.y)})`;
})()
""")
print("输入框:", info)

# 2. 清空
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return;
    el.focus();
    if (el.tagName === 'TEXTAREA') {
        el.select();
        el.value = '';
        el.dispatchEvent(new Event('input', {bubbles:true}));
    } else {
        el.textContent = '';
        el.dispatchEvent(new Event('input', {bubbles:true}));
    }
})()
""")
time.sleep(0.5)

# 3. 写入（textarea 走 setter，contenteditable 走 execCommand）
MSG = "【CDP千问测试】收到请回千问OK"
r = js(f"""
(() => {{
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    if (el.tagName === 'TEXTAREA') {{
        const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        s.call(el, {json.dumps(MSG)});
        el.dispatchEvent(new Event('input', {{bubbles:true}}));
    }} else {{
        document.execCommand('insertText', false, {json.dumps(MSG)});
    }}
    return el.value !== undefined ? el.value : el.innerText;
}})()
""")
print("写入后内容:", r)
time.sleep(0.8)

# 4. 检查内容还在吗
still = js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.value !== undefined ? el.value : el.innerText;
})()
""")
print(f"等待后内容: [{still[:60]}]  长度={len(still)}")
