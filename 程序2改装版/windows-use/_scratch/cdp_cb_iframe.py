import json, urllib.request, websocket

with urllib.request.urlopen("http://127.0.0.1:9223/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]

ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=15)
mid = 0
def js(code):
    global mid
    mid += 1
    ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r.get("result",{}).get("result",{}).get("value")

# 列出所有 iframe 的 URL
print("=== 主页面里的 iframe ===")
print(js("""
(() => {
    const ifrs = [...document.querySelectorAll('iframe')];
    return ifrs.map((f,i) => `[${i}] src="${f.src}" name="${f.name}" id="${f.id}" cls="${(f.className||'').toString().slice(0,40)}"`).join('\\n');
})()
"""))

# 用 CDP 命令列出所有 frame tree
print("\n=== CDP frame tree ===")
# 需要 Page.getFrameTree
mid += 1
ws.send(json.dumps({"id":mid,"method":"Page.getFrameTree"}))
while True:
    r = json.loads(ws.recv())
    if r.get("id") == mid:
        print(json.dumps(r.get("result",{}), indent=2, ensure_ascii=False)[:3000])
        break
