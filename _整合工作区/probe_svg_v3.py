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

# 诊断：报告页面规模 + 穿透 shadowRoot 抓 svg
JS = r"""
(() => {
  const stats = {
    elements: 0,
    svgs: 0,
    iframes: 0,
    shadowRoots: 0,
    iframe_details: [],
  };

  function scan(doc, path, depth) {
    if (!doc || depth > 10) return;
    let nodes;
    try { nodes = doc.querySelectorAll('*'); } catch (e) { return; }

    for (const el of nodes) {
      stats.elements++;
      // 穿透 shadowRoot
      if (el.shadowRoot) {
        stats.shadowRoots++;
        scan(el.shadowRoot, path + '/shadow(' + el.tagName + ')', depth + 1);
      }
      if (el.tagName === 'SVG') {
        stats.svgs++;
        const r = el.getBoundingClientRect();
        if (r.width > 0 && r.height > 0) {
          // 只记录有意义的（屏幕内的）
          if (r.y > 0 && r.y < 900 && r.x > 0 && r.x < 1400) {
            stats.svg_details = stats.svg_details || [];
            stats.svg_details.push({
              rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
              cls: (el.getAttribute('class') || '').slice(0, 60),
              rects: el.querySelectorAll('rect').length,
              paths: el.querySelectorAll('path').length,
              parentCls: el.parentElement ? (el.parentElement.className || '').toString().slice(0, 60) : '',
              grandCls: el.parentElement && el.parentElement.parentElement
                        ? (el.parentElement.parentElement.className || '').toString().slice(0, 60) : '',
            });
          }
        }
      }
      if (el.tagName === 'IFRAME') {
        stats.iframes++;
        stats.iframe_details.push({ idx: stats.iframes, src: (el.src || '').slice(0, 80) });
        try {
          const sub = el.contentDocument;
          if (sub) scan(sub, path + '/iframe', depth + 1);
        } catch (e) {}
      }
    }
  }

  scan(document, 'top', 0);
  return JSON.stringify(stats);
})()
"""

def get_pages():
    """返回所有 vscode-file page，优先聊天界面"""
    pages = [t for t in list_tabs(PORT)
             if t.get("type") == "page" and "vscode-file" in t.get("url", "")]
    return pages

pages = get_pages()
print("=" * 70)
print(f"找到 {len(pages)} 个 vscode-file page tab")
print("=" * 70)
for i, p in enumerate(pages):
    print(f"  [{i}] title={p.get('title','')[:50]}")
    print(f"       url={p.get('url','')[:100]}")
print()

# 对第一个聊天页做诊断
if not pages:
    print("❌ 没有 page，退出")
    exit(1)

# 判断哪个是聊天页：找标题里带具体项目名的
chat_page = None
for p in pages:
    title = p.get("title", "")
    if title and "CodeBuddy CN [管理员]" != title and "CodeBuddy CN" not in title[:20]:
        chat_page = p
        break
if not chat_page:
    chat_page = pages[0]

print(f"使用 page: {chat_page.get('title','')[:50]}")
print()

# 诊断
try:
    r = cdp_eval(chat_page["webSocketDebuggerUrl"], JS)
    if isinstance(r, str) and r.startswith("__JS_ERROR__"):
        print("❌ JS 异常：", r)
        exit(1)
    stats = json.loads(r)
    print("=" * 70)
    print("页面诊断")
    print("=" * 70)
    print(f"  元素总数    : {stats['elements']}")
    print(f"  SVG 总数    : {stats['svgs']}")
    print(f"  iframe 总数 : {stats['iframes']}")
    print(f"  shadowRoot  : {stats['shadowRoots']}")
    print()
    svg_details = stats.get("svg_details") or []
    print(f"  屏幕内 SVG  : {len(svg_details)}")
    for it in svg_details[:30]:
        print(f"    rect={it['rect']}  rect×{it['rects']} path×{it['paths']}")
        print(f"      cls   ={it['cls']}")
        print(f"      parent={it['parentCls']}")
        print(f"      grand ={it['grandCls']}")
except Exception as e:
    print("异常：", e)

print()
print("=" * 70)
print("进入监控 · 每 2 秒打印心跳 · Ctrl+C 退出")
print("=" * 70)
print("操作：给 CodeBuddy 发一个长任务，观察心跳输出变化")
print()

last_sig = None
hb = 0
while True:
    try:
        r = cdp_eval(chat_page["webSocketDebuggerUrl"], JS)
        if isinstance(r, str) and r.startswith("__JS_ERROR__"):
            print(f"  [heartbeat {hb}] JS 异常：{r[:120]}")
            time.sleep(2)
            hb += 1
            continue
        stats = json.loads(r)
        sig = json.dumps([(it['rect'], it['rects'], it['paths']) 
                          for it in (stats.get("svg_details") or [])])
        ts = time.strftime("%H:%M:%S")
        hb += 1
        if sig != last_sig:
            print(f"\n[{ts}] ⚡ SVG 结构变化 · 屏幕内 {len(stats.get('svg_details') or [])} 个")
            for it in (stats.get("svg_details") or [])[:20]:
                print(f"    rect={it['rect']} rect×{it['rects']} path×{it['paths']}  parent={it['parentCls'][:40]}")
            last_sig = sig
        else:
            # 心跳：只打印数字
            n = len(stats.get("svg_details") or [])
            print(f"\r[{ts}] hb={hb}  SVG={n}  元素={stats['elements']}  iframe={stats['iframes']}  shadow={stats['shadowRoots']}   ", end="")
    except Exception as e:
        print(f"\n异常：{e}")
    time.sleep(2)