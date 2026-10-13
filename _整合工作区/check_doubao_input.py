import json, urllib.request, websocket

def list_tabs(port):
    r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5)
    return json.loads(r.read().decode("utf-8"))

def cdp_eval(ws_url, js):
    ws = websocket.create_connection(ws_url, timeout=8)
    try:
        ws.send(json.dumps({"id":1,"method":"Runtime.evaluate",
            "params":{"expression":js,"returnByValue":True,"awaitPromise":False}}))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == 1:
                return resp.get("result",{}).get("result",{}).get("value")
    finally:
        ws.close()

JS = r"""
(() => {
  const out = [];
  for (const el of document.querySelectorAll('textarea, [contenteditable="true"], [role="textbox"], [class*="input"], [class*="editable"]')) {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;
    const text = el.value !== undefined ? el.value : (el.textContent || '');
    out.push({
      tag: el.tagName,
      cls: (el.className||'').toString().slice(0, 80),
      rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
      textLen: text.length,
      textHead: text.slice(0, 40),
      placeholder: el.getAttribute('placeholder') || '',
    });
  }
  return JSON.stringify(out);
})()
"""

for t in list_tabs(9231):
    if t.get("type") != "page": continue
    url = t.get("url","")
    if "doubao-chat" not in url and "doubao-launcher" not in url: continue
    print(f"=== {t.get('title','')[:40]}  {url[:60]} ===")
    try:
        r = cdp_eval(t["webSocketDebuggerUrl"], JS)
        items = json.loads(r) if r else []
        for it in items:
            print(f"  {it['tag']:10} rect={it['rect']}  textLen={it['textLen']}  ph={it['placeholder'][:20]}")
            print(f"      cls={it['cls']}")
            print(f"      text={it['textHead']}")
    except Exception as e:
        print(f"  异常：{e}")
    print()
