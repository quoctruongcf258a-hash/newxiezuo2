import json, urllib.request, websocket, time, sys

name = sys.argv[1]
PORT_MAP = {"QUEST":9224, "WorkBuddy":9227, "Qianwen":9226, "ZCode":9228, "Doubao":9225}
port = PORT_MAP[name]

with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
# 千问选含 qianwen.com 的页面
target = None
for p in pages:
    if name == "Qianwen" and "qianwen.com" in p.get("url",""):
        target = p; break
if target is None: target = pages[0]

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

print(f"=== {name} 端口{port} ===")
print("页面:", target.get("title"))

# 清空
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return;
    el.focus();
    el.textContent = ''; el.innerHTML = '';
})()
""")
time.sleep(0.3)

# 写入
js(f"""
(() => {{
    const el = document.querySelector('textarea, [contenteditable="true"]');
    el.focus();
    if (el.tagName === 'TEXTAREA') {{
        const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        s.call(el, '【{name}测】收到回{name} OK');
        el.dispatchEvent(new Event('input', {{bubbles:true}}));
    }} else {{
        document.execCommand('insertText', false, '【{name}测】收到回{name} OK');
    }}
}})()
""")
time.sleep(0.5)
print("写入后:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return (el.value !== undefined ? el.value : el.textContent).slice(0, 60);
})()
"""))

# 试5种发送方式
results = js("""
(() => {
    const inp = document.querySelector('textarea, [contenteditable="true"]');
    const ir = inp.getBoundingClientRect();
    const out = [];

    // 方式1：aria=发送
    let b = [...document.querySelectorAll('button')].find(x => (x.getAttribute('aria-label')||'') === '发送');
    if (b) { b.click(); out.push("aria发送-clicked"); } else out.push("aria发送-no");

    // 方式2：chat-input-v2-send-button
    b = document.querySelector('.chat-input-v2-send-button');
    if (b) { b.click(); out.push("chat-send-clicked"); } else out.push("chat-send-no");

    // 方式3：class含send的
    b = [...document.querySelectorAll('[class*="send"]')].find(x => /send[-_]?button/i.test((x.className||'').toString()));
    if (b) { b.click(); out.push("class-send-clicked"); } else out.push("class-send-no");

    return out.join(" | ");
})()
""")
print("试发送:", results)
time.sleep(1.5)
print("剩余字符:", js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el.value !== undefined ? el.value.length : el.textContent.length;
})()
"""))
