import json
import urllib.request
import websocket
import time

PORT = 9223

def list_tabs(port):
    r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5)
    return json.loads(r.read().decode("utf-8"))

def cdp_eval(ws_url, js, timeout=8):
    ws = websocket.create_connection(ws_url, timeout=timeout)
    try:
        ws.send(json.dumps({
            "id": 1, "method": "Runtime.evaluate",
            "params": {"expression": js, "returnByValue": True, "awaitPromise": False},
        }))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == 1:
                r = resp.get("result", {}).get("result", {})
                if r.get("subtype") == "error":
                    return "__JS_ERROR__: " + str(r.get("description", ""))[:300]
                return r.get("value")
    finally:
        ws.close()

# 递归穿透所有 iframe，抓 svg
JS = r"""
(() => {
  const all = [];

  function scan(doc, path) {
    if (!doc) return;
    let svgs;
    try { svgs = doc.querySelectorAll('svg'); } catch (e) { return; }
    for (let i = 0; i < svgs.length; i++) {
      const svg = svgs[i];
      let r;
      try { r = svg.getBoundingClientRect(); } catch (e) { continue; }
      if (r.width <= 0 || r.height <= 0) continue;
      all.push({
        path: path,
        idx: i,
        cls: (svg.getAttribute('class') || '').slice(0, 60),
        rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
        rects: svg.querySelectorAll('rect').length,
        paths: svg.querySelectorAll('path').length,
        circles: svg.querySelectorAll('circle').length,
        parentCls: svg.parentElement ? (svg.parentElement.className || '').toString().slice(0, 80) : '',
        grandCls: svg.parentElement && svg.parentElement.parentElement
                  ? (svg.parentElement.parentElement.className || '').toString().slice(0, 80) : '',
      });
    }
    // 继续扫描子 iframe
    let iframes;
    try { iframes = doc.querySelectorAll('iframe'); } catch (e) { return; }
    for (let j = 0; j < iframes.length; j++) {
      const ifr = iframes[j];
      let sub;
      try { sub = ifr.contentDocument; } catch (e) { continue; }
      if (sub) scan(sub, path + '/iframe[' + j + ']');
    }
  }

  scan(document, 'top');
  return JSON.stringify(all);
})()
"""

def get_page():
    for t in list_tabs(PORT):
        if t.get("type") == "page" and "vscode-file" in t.get("url", ""):
            return t
    return None

def snap():
    page = get_page()
    if not page:
        return "no-page"
    try:
        r = cdp_eval(page["webSocketDebuggerUrl"], JS)
        if isinstance(r, str) and r.startswith("__JS_ERROR__"):
            return r
        return json.loads(r) if r else []
    except Exception as e:
        return f"ERR: {e}"

print("=" * 70)
print("CodeBuddy SVG 穿透 iframe 监控 · 2 秒一次 · Ctrl+C 退出")
print("=" * 70)
print()
print("操作顺序：")
print("  1. 先啥都不做，看空闲态")
print("  2. 给 CodeBuddy 发一个长任务（写在输入框里，按发送）")
print("  3. 看运行态输出变化")
print("=" * 70)
print()

last_sig = None
while True:
    items = snap()
    if isinstance(items, str):
        print(f"  {items}")
        time.sleep(2)
        continue
    sig = json.dumps([(it['path'], it['rect'], it['rects'], it['paths']) for it in items])
    if sig != last_sig:
        ts = time.strftime("%H:%M:%S")
        print(f"\n[{ts}] 共 {len(items)} 个 svg：")
        for it in items:
            print(f"  {it['path']}[{it['idx']:3}]  rect={it['rect']}  "
                  f"rect×{it['rects']} path×{it['paths']} circ×{it['circles']}")
            print(f"      svg_cls   ={it['cls']}")
            print(f"      parent_cls={it['parentCls']}")
            print(f"      grand_cls ={it['grandCls']}")
        last_sig = sig
    time.sleep(2)