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
                    return "__ERR__: " + str(r.get("description", ""))[:200]
                return r.get("value")
    finally:
        ws.close()

# 快速体检：报告这个 tab 里有多少输入框、多少按钮
JS = r"""
(() => {
  let ta = 0, ce = 0, btn = 0, svg = 0, i = 0, img = 0;
  function scan(root) {
    if (!root) return;
    let nodes;
    try { nodes = root.querySelectorAll('*'); } catch (e) { return; }
    for (const el of nodes) {
      if (el.shadowRoot) scan(el.shadowRoot);
      const t = el.tagName;
      if (t === 'TEXTAREA') ta++;
      else if (t === 'INPUT') i++;
      else if (t === 'BUTTON') btn++;
      else if (t === 'SVG') svg++;
      else if (t === 'IMG') img++;
      if (el.getAttribute && el.getAttribute('contenteditable') === 'true') ce++;
    }
  }
  scan(document);
  return JSON.stringify({ta, ce, btn, svg, img, i, title: document.title});
})()
"""

tabs = list_tabs(PORT)
pages = [t for t in tabs if t.get("type") == "page" and not t.get("url", "").startswith("devtools")]

print("=" * 70)
print(f"共 {len(pages)} 个 page tab")
print("=" * 70)
print()

best = None
best_score = -1

for idx, p in enumerate(pages):
    title = p.get("title", "")[:40]
    url = p.get("url", "")[:60]
    try:
        r = cdp_eval(p["webSocketDebuggerUrl"], JS)
        if isinstance(r, str) and r.startswith("__ERR__"):
            print(f"[{idx}] {title}")
            print(f"    {url}")
            print(f"    ❌ {r[:100]}")
            continue
        d = json.loads(r)
        score = d['ta'] + d['ce'] * 2 + d['btn']
        print(f"[{idx}] {title}")
        print(f"    url={url}")
        print(f"    textarea={d['ta']}  contenteditable={d['ce']}  "
              f"button={d['btn']}  svg={d['svg']}  img={d['img']}  input={d['i']}")
        if score > best_score:
            best_score = score
            best = (idx, p)
    except Exception as e:
        print(f"[{idx}] {title}  ❌ {e}")

if not best:
    print("❌ 没找到合适 tab")
    exit(1)

print()
print("=" * 70)
print(f"✅ 选定 tab[{best[0]}] {best[1].get('title','')[:40]}")
print("=" * 70)

# 打印选定 tab 里所有输入框和按钮
JS2 = r"""
(() => {
  const out = [];
  function scan(root, depth) {
    if (!root || depth > 8) return;
    let nodes;
    try { nodes = root.querySelectorAll('*'); } catch (e) { return; }
    for (const el of nodes) {
      if (el.shadowRoot) scan(el.shadowRoot, depth + 1);
      const t = el.tagName;
      const isInput = t === 'TEXTAREA' || t === 'INPUT' ||
                       el.getAttribute('contenteditable') === 'true';
      const isBtn = t === 'BUTTON' || el.getAttribute('role') === 'button';
      if (!isInput && !isBtn) continue;
      const r = el.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) continue;
      const svg = el.querySelector('svg');
      out.push({
        kind: isInput ? 'INPUT' : 'BTN',
        tag: t,
        cls: (el.className || '').toString().slice(0, 70),
        aria: el.getAttribute('aria-label') || '',
        title: el.getAttribute('title') || '',
        rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
        hasSvg: !!svg,
        svgRects: svg ? svg.querySelectorAll('rect').length : 0,
        svgPaths: svg ? svg.querySelectorAll('path').length : 0,
        text: (el.textContent || '').trim().slice(0, 25),
      });
    }
  }
  scan(document, 0);
  return JSON.stringify(out);
})()
"""

p_best = best[1]
try:
    r = cdp_eval(p_best["webSocketDebuggerUrl"], JS2)
    items = json.loads(r) if r else []
    print(f"共 {len(items)} 个 INPUT / BTN：")
    print()
    for it in items:
        print(f"  {it['kind']:5} {it['tag']:10} rect={it['rect']}")
        print(f"        cls={it['cls']}")
        if it['aria']:  print(f"        aria={it['aria']}")
        if it['title']: print(f"        title={it['title']}")
        if it['text']:  print(f"        text={it['text']}")
        if it['hasSvg']:
            print(f"        svg: rect×{it['svgRects']} path×{it['svgPaths']}")
        print()
except Exception as e:
    print("异常：", e)