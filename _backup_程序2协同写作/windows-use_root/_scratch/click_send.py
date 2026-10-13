import json, urllib.request, websocket, time, sys

def try_one(name, port):
    print(f"\n=== {name} (端口{port}) ===")
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
            pages = [t for t in json.load(f) if t.get("type")=="page"]
    except Exception as e:
        print(f"  ❌ 端口不通"); return
    t = pages[0]
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

    # 1. 清空+写入
    js(f"""
    (() => {{
        const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
        if (!el) return;
        el.focus();
        if (el.tagName === 'TEXTAREA') {{
            el.select();
            const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
            s.call(el, '');
            el.dispatchEvent(new Event('input', {{bubbles:true}}));
        }} else {{
            el.textContent = '';
        }}
    }})()
    """)
    time.sleep(0.3)
    js(f"""
    (() => {{
        const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
        el.focus();
        if (el.tagName === 'TEXTAREA') {{
            const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
            s.call(el, '【按钮测】{name} 收到回OK');
            el.dispatchEvent(new Event('input', {{bubbles:true}}));
        }} else {{
            document.execCommand('insertText', false, '【按钮测】{name} 收到回OK');
        }}
    }})()
    """)
    time.sleep(0.5)

    # 2. 找输入框右边/下方的按钮，点最近的那个
    r = js("""
    (() => {
        const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
        const er = el.getBoundingClientRect();
        const cands = [...document.querySelectorAll('button, [role="button"], div[class*="send"], div[class*="send"] *, svg')];
        const near = cands.filter(b => {
            const r = b.getBoundingClientRect();
            if (r.width === 0 || r.height === 0) return false;
            const dy = r.y - er.y;
            const dx = r.x - (er.x + er.width);
            return dy > -30 && dy < 80 && dx > -20 && dx < 200;
        });
        if (!near.length) return "no-btn";
        // 点最右下的那个
        near.sort((a,b) => (b.getBoundingClientRect().x - a.getBoundingClientRect().x));
        const btn = near[0];
        const br = btn.getBoundingClientRect();
        const ev = btn.tagName === 'svg' ? btn.parentElement : btn;
        ev.click();
        return `clicked ${ev.tagName} at (${Math.round(br.x)},${Math.round(br.y)})`;
    })()
    """)
    print(f"  点击: {r}")

for name, port in [("QUEST",9224),("Doubao",9225),("WorkBuddy",9227),("ZCode",9228)]:
    try_one(name, port)
