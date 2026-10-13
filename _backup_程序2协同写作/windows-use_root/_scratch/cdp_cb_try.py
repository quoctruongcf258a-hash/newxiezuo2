import json, urllib.request, websocket, time

with urllib.request.urlopen("http://127.0.0.1:9223/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]

ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=15)
mid = 0
def cmd(method, **params):
    global mid
    mid += 1
    ws.send(json.dumps({"id":mid,"method":method,"params":params}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r

def js(code, ctx=None):
    p = {"expression":code, "returnByValue":True}
    if ctx: p["contextId"] = ctx
    r = cmd("Runtime.evaluate", **p)
    return r.get("result",{}).get("result",{}).get("value")

# 1. 试直接进 iframe 的 contentDocument
print("=== 试 iframe.contentDocument ===")
print(js("""
(() => {
    const ifrs = [...document.querySelectorAll('iframe')];
    let out = [];
    for (let i=0; i<ifrs.length; i++) {
        try {
            const d = ifrs[i].contentDocument;
            if (!d) { out.push(`[${i}] contentDocument=null`); continue; }
            const ta = d.querySelectorAll('textarea').length;
            const ce = d.querySelectorAll('[contenteditable="true"]').length;
            out.push(`[${i}] ✅ 能进！textarea=${ta} contenteditable=${ce}`);
        } catch (e) {
            out.push(`[${i}] ❌ 跨域: ${e.message}`);
        }
    }
    return out.join('\\n');
})()
"""))

# 2. 列出 CDP 能看到的所有 execution context
print("\n=== CDP 的 execution contexts ===")
r = cmd("Runtime.enable")
time.sleep(0.5)
# 收集事件
contexts = []
start = time.time()
while time.time() - start < 1:
    try:
        ws.settimeout(0.2)
        m = json.loads(ws.recv())
        if m.get("method") == "Runtime.executionContextCreated":
            c = m["params"]["context"]
            contexts.append(c)
    except: pass
ws.settimeout(15)
for c in contexts:
    name = c.get("name","")
    origin = c.get("origin","")
    aux = c.get("auxData",{})
    print(f"  ctx id={c['id']}  name=[{name[:40]}]  origin=[{origin[:60]}]  isDefault={aux.get('isDefault')}")
