import sys, time
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")

APPS = {
    "QUEST":     (9224, ""),
    "Doubao":    (9225, ""),
    "WorkBuddy": (9227, ""),
    "ZCode":     (9228, ""),
    "Qianwen":   (9226, ""),
}

import json, urllib.request, websocket

def try_one(name, port):
    print(f"\n=== {name} (端口{port}) ===")
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
            pages = [t for t in json.load(f) if t.get("type")=="page"]
    except Exception as e:
        print(f"  ❌ 端口不通: {e}"); return
    if not pages:
        print("  ❌ 无页面"); return
    t = pages[0]
    print(f"  页面: {t.get('title','')[:40]}")
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=15)
    mid = 0
    def js(code):
        nonlocal mid
        mid += 1
        ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == mid:
                return r.get("result",{}).get("result",{}).get("value")
    # 找输入框
    info = js("""
    (() => {
        const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
        if (!el) return "no-input";
        return `tag=${el.tagName} cls="${(el.className||'').toString().slice(0,40)}"`;
    })()
    """)
    print(f"  输入框: {info}")
    # 写入
    w = js(f"""
    (() => {{
        const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
        if (!el) return "no-input";
        el.focus();
        if (el.tagName === 'TEXTAREA') {{
            const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
            s.call(el, "【单测】{name} 收到回OK");
            el.dispatchEvent(new Event('input', {{bubbles:true}}));
        }} else {{
            document.execCommand('insertText', false, "【单测】{name} 收到回OK");
        }}
        return "ok";
    }})()
    """)
    print(f"  写入: {w}")
    time.sleep(0.5)
    # 回车
    e = js("""
    (() => {
        const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
        if (!el) return "no-input";
        el.focus();
        const o = {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true, cancelable:true};
        el.dispatchEvent(new KeyboardEvent('keydown', o));
        el.dispatchEvent(new KeyboardEvent('keypress', o));
        el.dispatchEvent(new KeyboardEvent('keyup', o));
        return "ok";
    })()
    """)
    print(f"  回车: {e}")

for name, (port, _) in APPS.items():
    try_one(name, port)
