import json, urllib.request, websocket, time

PORT = 9223
with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=5) as f:
    tabs = json.load(f)
iframes = [t for t in tabs if t.get("type")=="iframe"]

for i, fr in enumerate(iframes):
    print(f"\n=== iframe[{i}] ===")
    ws = websocket.create_connection(fr["webSocketDebuggerUrl"], timeout=10)
    mid = 0
    def cmd(method, **params):
        global mid
        mid += 1
        ws.send(json.dumps({"id":mid,"method":method,"params":params}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == mid: return r
    def js(code):
        r = cmd("Runtime.evaluate", expression=code, returnByValue=True)
        return r.get("result",{}).get("result",{}).get("value")

    # 看 frame tree
    cmd("Page.enable")
    r = cmd("Page.getFrameTree")
    def walk(f, d=0):
        fr2 = f["frame"]
        print("  "*d + f"  frame: {fr2.get('url','')[:80]}")
        for c in f.get("childFrames", []): walk(c, d+1)
    print("  --- frames ---")
    try: walk(r["result"]["frameTree"])
    except: print("  无 frame tree")

    # 列出所有 iframe
    print("  --- 内层 iframe ---")
    print(js("""
    (() => {
        const ifrs = [...document.querySelectorAll('iframe')];
        return ifrs.map((f,i) => `[${i}] src="${(f.src||'').slice(0,80)}"`).join('\\n') || '无';
    })()
    """))

    # 看有没有 vscode-webview 挂载点
    print("  --- 可能的挂载点 ---")
    print(js("""
    (() => {
        const cands = ['vscode-webview','webview','main','root','app','#root','[data-vscode]'];
        let out = [];
        for (const s of cands) {
            const els = document.querySelectorAll(s);
            els.forEach((el,i) => out.push(`${s}[${i}] tag=${el.tagName} children=${el.children.length} innerText=${(el.innerText||'').slice(0,50)}`));
        }
        return out.slice(0, 20).join('\\n') || '无';
    })()
    """))

    # 抓所有有文本的元素（找聊天区）
    print("  --- 页面有文本的元素（top 10） ---")
    print(js("""
    (() => {
        const all = [...document.querySelectorAll('*')].filter(el => {
            const t = (el.innerText || '').trim();
            return t.length > 3 && t.length < 300 && el.children.length < 3;
        });
        return all.slice(0, 10).map((el,i) => `[${i}] <${el.tagName}> "${(el.innerText||'').slice(0,60).replace(/\\n/g,' ')}"`).join('\\n') || '无';
    })()
    """))
    ws.close()
