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
                    return "__ERR__:" + str(r.get("description",""))[:150]
                return r.get("value")
    finally:
        ws.close()

# 抓 rect=[349,484] 和 [377,484] 附近 10px 内的元素（页面坐标，视口坐标）
JS = r"""
(() => {
  const targets = [[349,484],[377,484]];
  const out = [];
  for (const el of document.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;
    const cx = r.x + r.width/2, cy = r.y + r.height/2;
    for (const [tx,ty] of targets) {
      if (Math.hypot(cx-tx, cy-ty) < 15) {
        const svg = el.querySelector('svg');
        let svgHtml = svg ? svg.outerHTML.slice(0, 250) : '';
        out.push({
          target: [tx,ty],
          tag: el.tagName,
          cls: (el.className || '').toString(),
          rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
          bg: getComputedStyle(el).backgroundColor,
          svgHtml: svgHtml,
          disabled: (el.className||'').toString().includes('disabled'),
        });
        break;
      }
    }
  }
  return JSON.stringify(out);
})()
"""

def get_chat_page():
    """每次调用都重新拿一次，防刷新后 webSocketDebuggerUrl 失效"""
    for t in list_tabs(PORT):
        if t.get("type") == "page" and "vscode-file" in t.get("url", ""):
            # 优先 title 带具体项目名（不是 "CodeBuddy CN [管理员]"）
            title = t.get("title", "")
            if title and "CodeBuddy CN [管理员]" != title:
                return t
    # 兜底：随便一个 vscode-file
    for t in list_tabs(PORT):
        if t.get("type") == "page" and "vscode-file" in t.get("url", ""):
            return t
    return None

def snap():
    page = get_chat_page()
    if not page:
        return None
    try:
        r = cdp_eval(page["webSocketDebuggerUrl"], JS)
        if isinstance(r, str) and r.startswith("__ERR__"):
            return r
        return json.loads(r) if r else []
    except Exception as e:
        return f"ERR:{e}"

print("=" * 70)
print("CodeBuddy 发送/停止按钮监控 · 1 秒一次 · Ctrl+C 退出")
print("=" * 70)
print("操作顺序：")
print("  1. 现在什么都不做，看空闲态（两个按钮都是灰的/禁用的）")
print("  2. 在输入框打几个字 —— 发送按钮应该变紫色（enabled）")
print("  3. 点发送 —— 按钮应该变成方块（stop）")
print("  4. 等它答完 —— 变回纸飞机")
print("=" * 70)
print()

last_sig = None
hb = 0
while True:
    items = snap()
    hb += 1
    ts = time.strftime("%H:%M:%S")
    if items is None:
        print(f"\r[{ts}] hb={hb}  拿不到 page", end="")
    elif isinstance(items, str):
        print(f"\r[{ts}] hb={hb}  {items[:80]}", end="")
    else:
        # 用 target + cls + svg 签名
        sig = json.dumps([(it['target'], it['cls'], it['disabled'], len(it['svgHtml'])) 
                          for it in items])
        if sig != last_sig:
            print(f"\n\n[{ts}] ⚡ 按钮状态变化：")
            for it in items:
                print(f"  target={it['target']}  tag={it['tag']}  rect={it['rect']}")
                print(f"    cls      = {it['cls']}")
                print(f"    disabled = {it['disabled']}")
                print(f"    bg       = {it['bg']}")
                print(f"    svg      = {it['svgHtml'][:200]}")
                print()
            last_sig = sig
        else:
            n = len(items)
            flags = "".join("D" if it['disabled'] else "E" for it in items)
            print(f"\r[{ts}] hb={hb}  按钮={n}  状态={flags}   ", end="")
    time.sleep(1)