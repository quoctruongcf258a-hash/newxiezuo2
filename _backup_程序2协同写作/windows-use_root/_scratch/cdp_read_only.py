import json, urllib.request, time
import websocket

with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=5) as f:
    tabs = [t for t in json.load(f) if t.get("type")=="page"]
target = [t for t in tabs if "sign_in" not in t.get("url","")][0]
ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
mid = 0
def js(code):
    global mid
    mid += 1
    ws.send(json.dumps({"id": mid, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r.get("result", {}).get("result", {}).get("value")

print("标题:", js("document.title"))
print("\n=== assistant 容器内容 ===")
print(js("""
(() => {
    const sels = [
        '[class*="assistant"][class*="message"]',
        '[class*="message"][class*="assistant"]',
        '[class*="assistant-message"]',
        '[data-role="assistant"]',
        '[class*="bot-message"]',
    ];
    for (const s of sels) {
        const els = document.querySelectorAll(s);
        if (els.length) {
            return `选择器: ${s}\\n数量: ${els.length}\\n\\n最后一条:\\n` + els[els.length-1].innerText;
        }
    }
    return "全都没找到";
})()
"""))
