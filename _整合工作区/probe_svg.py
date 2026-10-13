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
                r = resp.get("result", {}).get("result", {})
                if r.get("subtype") == "error":
                    return "__JS_ERROR__: " + str(r.get("description", ""))[:300]
                return r.get("value")
    finally:
        ws.close()

# 简单粗暴：抓所有 svg，输出：位置 + 内部的 rect/path/circle 数量
JS = r"""
(() => {
  const out = [];
  const svgs = document.querySelectorAll('svg');
  for (let i = 0; i < svgs.length; i++) {
    const svg = svgs[i];
    const r = svg.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;
    const rects = svg.querySelectorAll('rect').length;
    const paths = svg.querySelectorAll('path').length;
    const circles = svg.querySelectorAll('circle').length;
    const lines = svg.querySelectorAll('line').length;
    const polygons = svg.querySelectorAll('polygon').length;
    // 取第一个 path 的 d 前 40 字
    let firstD = '';
    const p0 = svg.querySelector('path');
    if (p0) firstD = (p0.getAttribute('d') || '').slice(0, 40);
    out.push({
      i: i,
      cls: (svg.getAttribute('class') || '').slice(0, 60),
      rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
      rects: rects, paths: paths, circles: circles, lines: lines, polygons: polygons,
      firstD: firstD,
      parentCls: svg.parentElement ? (svg.parentElement.className || '').toString().slice(0, 60) : '',
      grandCls: svg.parentElement && svg.parentElement.parentElement
                ? (svg.parentElement.parentElement.className || '').toString().slice(0, 60) : '',
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
        return "no-page"
    try:
        r = cdp_eval(page["webSocketDebuggerUrl"], JS)
        if isinstance(r, str) and r.startswith("__JS_ERROR__"):
            return r
        return json.loads(r) if r else []
    except Exception as e:
        return f"ERR: {e}"

print("=" * 70)
print("CodeBuddy SVG 形状监控 · 2 秒一次 · Ctrl+C 退出")
print("=" * 70)
print("现在啥都别做，先看空闲态")
print("然后给 CodeBuddy 发长任务，看运行态")
print("=" * 70)
print()

last_sig = None
while True:
    items = snap()
    if isinstance(items, str):
        print(f"  {items}")
        time.sleep(2)
        continue
    # 只打印 svg 数量 + 关键几个
    sig = json.dumps([(it['rect'], it['rects'], it['paths'], it['circles']) for it in items])
    if sig != last_sig:
        ts = time.strftime("%H:%M:%S")
        print(f"\n[{ts}] 共 {len(items)} 个 svg：")
        for it in items:
            print(f"  [{it['i']:3}] rect={it['rect']}  "
                  f"rect×{it['rects']} path×{it['paths']} circ×{it['circles']} "
                  f"line×{it['lines']} poly×{it['polygons']}")
            print(f"       svg_cls={it['cls']}")
            print(f"       parent={it['parentCls']}")
            print(f"       grand ={it['grandCls']}")
            if it['firstD']:
                print(f"       path_d={it['firstD']}")
        last_sig = sig
    time.sleep(2)