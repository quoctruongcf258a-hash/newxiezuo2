import json, urllib.request, websocket, time

PORT = 9223

# 1. 看主 target 的所有子目标
with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=5) as f:
    tabs = json.load(f)

print("=== 所有 targets ===")
for t in tabs:
    print(f"  type={t.get('type'):10}  title={t.get('title','')[:40]}")
    print(f"      url={t.get('url','')[:90]}")
    print(f"      ws={t.get('webSocketDebuggerUrl','')[:80]}")

# 2. 如果 page 只有 1 个，那 webview 也在其中——用 Page.getFrameTree 深挖
pages = [t for t in tabs if t.get("type")=="page"]
if not pages:
    print("没页面"); exit()

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

# Page.enable 后才能拿到 frame 事件
cmd("Page.enable")
cmd("Runtime.enable")
time.sleep(0.5)

# 递归列出所有 frame
r = cmd("Page.getFrameTree")
def walk(f, depth=0):
    fr = f["frame"]
    print("  " * depth + f"frame id={fr['id'][:12]}  url={fr.get('url','')[:70]}")
    for c in f.get("childFrames", []):
        walk(c, depth+1)

print("\n=== Frame Tree ===")
walk(r["result"]["frameTree"])

# 收集 execution context 事件
print("\n=== 监听 3 秒收集 context 事件 ===")
ws.settimeout(3)
contexts = []
try:
    while True:
        m = json.loads(ws.recv())
        if m.get("method") == "Runtime.executionContextCreated":
            contexts.append(m["params"]["context"])
except: pass
ws.settimeout(15)

print(f"共 {len(contexts)} 个 context")
for c in contexts:
    aux = c.get("auxData", {})
    print(f"  id={c['id']}  default={aux.get('isDefault')}  frameId={aux.get('frameId','')[:12]}  origin=[{c.get('origin','')[:50]}]  name=[{c.get('name','')[:30]}]")
