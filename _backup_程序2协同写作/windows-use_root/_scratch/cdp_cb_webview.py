import json, urllib.request, websocket, time

PORT = 9223
with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=5) as f:
    tabs = json.load(f)

# 找所有 iframe target
iframes = [t for t in tabs if t.get("type") == "iframe"]
print(f"发现 {len(iframes)} 个 iframe target")

for i, fr in enumerate(iframes):
    print(f"\n=== iframe[{i}] ===")
    print(f"  url: {fr.get('url','')[:100]}")
    ws_url = fr.get("webSocketDebuggerUrl")
    if not ws_url:
        print("  没 WS"); continue
    try:
        ws = websocket.create_connection(ws_url, timeout=10)
        mid = 0
        def js(code):
            global mid
            mid += 1
            ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
            while True:
                r = json.loads(ws.recv())
                if r.get("id") == mid:
                    return r.get("result",{}).get("result",{}).get("value")
        title = js("document.title")
        print(f"  title: {title}")
        info = js("""
        (() => {
            const ta = document.querySelectorAll('textarea').length;
            const ce = document.querySelectorAll('[contenteditable="true"]').length;
            const rt = document.querySelectorAll('[role="textbox"]').length;
            const btns = document.querySelectorAll('button').length;
            const txt = (document.body.innerText || '').slice(0, 100).replace(/\\n/g, ' ');
            return `textarea=${ta} contenteditable=${ce} role=textbox=${rt} button=${btns}\\n前100字: ${txt}`;
        })()
        """)
        print(f"  DOM: {info}")
        ws.close()
    except Exception as e:
        print(f"  ❌ {e}")
