import json, urllib.request, websocket

with urllib.request.urlopen("http://127.0.0.1:9226/json", timeout=5) as f:
    pages = [t for t in json.load(f) if t.get("type")=="page"]
# 选含 qianwen.com 的
target = None
for p in pages:
    if "qianwen.com" in p.get("url",""):
        target = p; break
if not target: target = pages[0]
print("连接:", target.get("title"), "|", target.get("url"))

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

# 找输入框附近的所有 button / svg
print("\n=== 输入框附近的按钮 ===")
print(js("""
(() => {
    const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
    if (!el) return "no-input";
    let node = el, found = new Set();
    for (let i=0; i<8 && node; i++) {
        node.querySelectorAll('button, [role="button"], div[class*="send"], svg').forEach(b => found.add(b));
        node = node.parentElement;
    }
    return [...found].map((b,i) => {
        const r = b.getBoundingClientRect();
        const cls = (b.className||'').toString().slice(0,50);
        const tag = b.tagName;
        const dis = b.disabled;
        return `[${i}] ${tag} disabled=${dis} cls="${cls}" pos=(${Math.round(r.x)},${Math.round(r.y)}) ${Math.round(r.width)}x${Math.round(r.height)}`;
    }).join('\\n');
})()
"""))
