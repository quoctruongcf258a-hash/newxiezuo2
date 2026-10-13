import json, urllib.request, time, websocket

PORT = 9228
with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=5) as f:
    tabs = [t for t in json.load(f) if t.get("type")=="page"]

target = tabs[0]
ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15)
mid = 0
def js(code):
    global mid
    mid += 1
    ws.send(json.dumps({"id": mid, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            res = r.get("result", {}).get("result", {})
            return res.get("value")

print("标题:", js("document.title"))

# 找输入框（找所有可编辑元素）
print("\n=== 输入框候选 ===")
print(js("""
(() => {
    const sels = ['textarea', '[contenteditable="true"]', '[role="textbox"]', 'input[type="text"]'];
    let out = [];
    for (const s of sels) {
        const els = document.querySelectorAll(s);
        els.forEach((el,i) => out.push(`${s}[${i}] tag=${el.tagName} ph="${el.placeholder||''}" cls="${(el.className||'').toString().slice(0,40)}"`));
    }
    return out.join('\\n') || '没找到';
})()
"""))

# 找发送按钮
print("\n=== 发送按钮候选 ===")
print(js("""
(() => {
    const btns = [...document.querySelectorAll('button, [role="button"]')];
    const cands = btns.filter(b => /发送|send|submit/i.test((b.textContent||'')+(b.getAttribute('aria-label')||'')));
    if (!cands.length) return '没找到';
    return cands.map((b,i) => `[${i}] text="${b.textContent.trim().slice(0,15)}"`).join('\\n');
})()
"""))

# 写入测试
MSG = "【CDP测试】你好，请回 OK"
print(f"\n写入: {MSG}")
print(js(f"""
(() => {{
    const el = document.querySelector('textarea, [contenteditable="true"]');
    if (!el) return "❌ 没输入框";
    el.focus();
    if (el.tagName === 'TEXTAREA') {{
        const s = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        s.call(el, {json.dumps(MSG)});
        el.dispatchEvent(new Event('input', {{bubbles: true}}));
    }} else {{
        document.execCommand('insertText', false, {json.dumps(MSG)});
    }}
    return "✅ 已写入";
}})()
"""))
