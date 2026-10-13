import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9226/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
target = [p for p in pages if "qianwen.com" in p.get("url","")]
target = target[0] if target else pages[0]

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

# 清空 + 写入
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
    if (el) { el.focus(); document.execCommand('selectAll'); document.execCommand('delete'); }
})()
""")
time.sleep(0.3)
js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
    el.focus();
    if (el.tagName === 'TEXTAREA') {
        const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        s.call(el, '【CDP测试-CtrlEnter】收到回OK');
        el.dispatchEvent(new Event('input', {bubbles:true}));
    } else {
        document.execCommand('insertText', false, '【CDP测试-CtrlEnter】收到回OK');
    }
})()
""")
time.sleep(0.5)

# Ctrl+Enter
print("=== Ctrl+Enter ===")
print(js("""
(() => {
    const el = document.activeElement;
    const ctrl = {ctrlKey:true, bubbles:true, cancelable:true};
    el.dispatchEvent(new KeyboardEvent('keydown', {...ctrl, key:'Enter', code:'Enter', keyCode:13, which:13}));
    el.dispatchEvent(new KeyboardEvent('keypress', {...ctrl, key:'Enter', code:'Enter', keyCode:13, which:13}));
    el.dispatchEvent(new KeyboardEvent('keyup', {...ctrl, key:'Enter', code:'Enter', keyCode:13, which:13}));
    return "已发";
})()
"""))
time.sleep(1.5)
left = js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"]');
    return el ? (el.value !== undefined ? el.value : el.innerText).length : -1;
})()
""")
print(f"输入框剩余字符: {left}")
