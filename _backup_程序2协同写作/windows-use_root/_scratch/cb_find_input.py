import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9223/json", timeout=5) as f:
    tabs = json.load(f)

iframes = [t for t in tabs if t.get("type")=="iframe"]
print(f"共 {len(iframes)} 个 iframe，逐个检查...\n")

for i, fr in enumerate(iframes):
    print(f"[{i}] {fr.get('url','')[:70]}")
    try:
        ws = websocket.create_connection(fr["webSocketDebuggerUrl"], timeout=8)
        mid = 0
        def js(code):
            global mid
            mid += 1
            ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
            while True:
                r = json.loads(ws.recv())
                if r.get("id") == mid:
                    return r.get("result",{}).get("result",{}).get("value")
        n_ta = js("document.querySelectorAll('textarea').length") or 0
        n_ce = js("document.querySelectorAll('[contenteditable=\"true\"]').length") or 0
        n_btn = js("document.querySelectorAll('button').length") or 0
        n_all = js("document.querySelectorAll('*').length") or 0
        title = js("document.title") or ""
        body_head = (js("document.body ? document.body.innerText.slice(0,80) : ''") or "").replace("\n", " ")
        mark = "🎯" if (n_ta + n_ce) > 0 else "  "
        print(f"   {mark} title={title[:40]}")
        print(f"      ta={n_ta} ce={n_ce} btn={n_btn} 总={n_all}")
        print(f"      body前80: {body_head}")
        ws.close()
    except Exception as e:
        print(f"   ❌ {e}")
    print()
