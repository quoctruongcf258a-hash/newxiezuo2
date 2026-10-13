import json, urllib.request, websocket

APPS = {
    "CodeBuddy": 9223, "QUEST": 9224, "Doubao": 9225,
    "Qianwen": 9226, "WorkBuddy": 9227, "ZCode": 9228,
}

def probe(name, port):
    print(f"\n{'='*60}\n{name}  port {port}\n{'='*60}")
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
            pages = [t for t in json.load(f) if t.get("type")=="page"]
    except Exception as e:
        print("  连不上:", e); return

    print(f"  共 {len(pages)} 个 page")
    for i, p in enumerate(pages):
        print(f"    [{i}] title={p.get('title','')[:40]}")
        print(f"        url={p.get('url','')[:80]}")

    # 逐个尝试连上并检查 DOM
    for i, p in enumerate(pages):
        print(f"\n  --- page[{i}] ---")
        try:
            ws = websocket.create_connection(p["webSocketDebuggerUrl"], timeout=10)
            mid = 0
            def js(code):
                nonlocal mid
                mid += 1
                ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
                while True:
                    r = json.loads(ws.recv())
                    if r.get("id") == mid:
                        return r.get("result",{}).get("result",{}).get("value")
            title = js("document.title")
            print(f"      title: {title}")
            # 数输入框
            n = js("""
            (() => {
                const ta = document.querySelectorAll('textarea').length;
                const ce = document.querySelectorAll('[contenteditable="true"]').length;
                const rt = document.querySelectorAll('[role="textbox"]').length;
                const ifr = document.querySelectorAll('iframe').length;
                const sh = document.querySelectorAll('*').length;
                return `textarea=${ta} contenteditable=${ce} role=textbox=${rt} iframe=${ifr} 总元素=${sh}`;
            })()
            """)
            print(f"      DOM: {n}")
            # 输入框具体信息
            info = js("""
            (() => {
                const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
                if (!el) return 'none';
                const r = el.getBoundingClientRect();
                return `${el.tagName} ph="${el.placeholder||''}" cls="${(el.className||'').toString().slice(0,40)}" pos=(${Math.round(r.x)},${Math.round(r.y)}) size=${Math.round(r.width)}x${Math.round(r.height)}`;
            })()
            """)
            print(f"      输入框: {info}")
            ws.close()
        except Exception as e:
            print(f"      ❌ {e}")

for name, port in APPS.items():
    probe(name, port)
