import json
import urllib.request
import websocket
import time

PORT = 9223

def list_tabs(port):
    r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5)
    return json.loads(r.read().decode("utf-8"))

def cdp_eval(ws_url, js, timeout=5):
    ws = websocket.create_connection(ws_url, timeout=timeout)
    try:
        ws.send(json.dumps({
            "id": 1, "method": "Runtime.evaluate",
            "params": {"expression": js, "returnByValue": True, "awaitPromise": False},
        }))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == 1:
                return resp.get("result", {}).get("result", {}).get("value")
    finally:
        ws.close()

# 抓输入框附近（y 450-540）所有元素，含 svg / path 完整信息
JS = r"""
(() => {
  const out = [];
  for (const el of document.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;
    if (r.y < 440 || r.y > 560) continue;
    if (r.x < 300 || r.x > 700) continue;
    if (r.width < 16 || r.width > 60) continue;
    if (r.height < 16 || r.height > 60) continue;

    const cls = (el.className || '').toString();
    const svg = el.querySelector('svg');
    const svgPaths = svg ? Array.from(svg.querySelectorAll('path, rect, polygon, line'))
        .map(p => p.getAttribute('d') || p.getAttribute('points') || 
                  (p.tagName + ' ' + (p.getAttribute('width')||'') + 'x' + (p.getAttribute('height')||'')))
        .slice(0, 4) : [];

    out.push({
      tag: el.tagName,
      cls: cls.slice(0, 120),
      aria: el.getAttribute('aria-label') || '',
      title: el.getAttribute('title') || '',
      dataIcon: el.getAttribute('data-icon') || '',
      rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
      bg: getComputedStyle(el).backgroundColor,
      svgViewBox: svg ? (svg.getAttribute('viewBox') || '') : '',
      svgCls: svg ? (svg.getAttribute('class') || '') : '',
      svgPaths: svgPaths,
      html: el.outerHTML.slice(0, 400),
    });
  }
  return JSON.stringify(out);
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
        return None
    try:
        r = cdp_eval(page["webSocketDebuggerUrl"], JS)
        return json.loads(r) if r else None
    except Exception:
        return None

print("=" * 70)
print("抓取 CodeBuddy 输入框附近元素 · 每 2 秒一次 · Ctrl+C 退出")
print("=" * 70)
print()
print("操作顺序：")
print("  1. 现在什么都不做，看空闲态输出")
print("  2. 给 CodeBuddy 发一个长任务")
print("  3. 看运行中输出，对比两组变化")
print("=" * 70)
print()

last_sig = None
while True:
    items = snap()
    if not items:
        time.sleep(2)
        continue
    sig = json.dumps([(it['cls'], it['aria'], tuple(it['rect'])) for it in items])
    if sig != last_sig:
        ts = time.strftime("%H:%M:%S")
        print(f"\n[{ts}] 共 {len(items)} 个元素：")
        for it in items:
            print(f"  ── {it['tag']} cls={it['cls'][:60]}")
            print(f"     rect={it['rect']}  bg={it['bg']}")
            if it['aria']:    print(f"     aria={it['aria']}")
            if it['title']:   print(f"     title={it['title']}")
            if it['dataIcon']:print(f"     data-icon={it['dataIcon']}")
            if it['svgCls']:  print(f"     svg_cls={it['svgCls']}")
            if it['svgViewBox']: print(f"     svg_viewBox={it['svgViewBox']}")
            if it['svgPaths']:
                for p in it['svgPaths']:
                    print(f"     path: {p[:80]}")
            print(f"     html: {it['html'][:200]}")
        last_sig = sig
    time.sleep(2)