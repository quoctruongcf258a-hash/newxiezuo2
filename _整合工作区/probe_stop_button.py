import json
import sys
import urllib.request
import websocket   # pip install websocket-client
from pathlib import Path

# 读 today.json 拿端口
TODAY = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\today.json")
data = json.loads(TODAY.read_text(encoding="utf-8"))

def cdp_eval(port, js, timeout=5):
    """在 CDP 目标页面执行 JS，返回结果。"""
    # 拿 webSocketDebuggerUrl
    r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=timeout)
    tabs = json.loads(r.read().decode("utf-8"))
    page = None
    for t in tabs:
        if t.get("type") == "page" and not t.get("url", "").startswith("devtools"):
            page = t
            break
    if not page:
        return None
    ws_url = page["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url, timeout=timeout)
    try:
        cmd = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": js,
                "returnByValue": True,
                "awaitPromise": False,
            },
        }
        ws.send(json.dumps(cmd))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == 1:
                return resp.get("result", {}).get("result", {}).get("value")
    finally:
        ws.close()

# 找页面里所有"可能是停止按钮"的元素
JS = r"""
(() => {
  const out = [];
  const kws = ['stop', '停止', '中止', '暂停', 'pause', 'abort', 'cancel', '取消', '生成中', 'generating'];
  const all = document.querySelectorAll('button, [role="button"], [aria-label], [title], [data-testid]');
  for (const el of all) {
    const attrs = [
      el.getAttribute('aria-label'),
      el.getAttribute('title'),
      el.getAttribute('data-testid'),
      el.getAttribute('data-icon'),
      el.className ? el.className.toString() : '',
      el.id || '',
      el.tagName
    ].filter(Boolean).join(' | ').toLowerCase();
    let hit = false;
    for (const kw of kws) {
      if (attrs.includes(kw.toLowerCase())) { hit = true; break; }
    }
    if (!hit) continue;
    const r = el.getBoundingClientRect();
    const st = getComputedStyle(el);
    if (r.width <= 0 || r.height <= 0) continue;
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    out.push({
      tag: el.tagName,
      cls: (el.className || '').toString().slice(0, 80),
      id: el.id || '',
      aria: el.getAttribute('aria-label') || '',
      title: el.getAttribute('title') || '',
      testid: el.getAttribute('data-testid') || '',
      rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
      text: (el.textContent || '').trim().slice(0, 40),
    });
  }
  return JSON.stringify(out);
})()
"""

for item in data.get("opened", []):
    port = item.get("cdpPort")
    label = item.get("label") or item.get("key")
    if not port:
        continue
    print("=" * 70)
    print(f"{label}  (端口 {port})")
    print("=" * 70)
    try:
        result = cdp_eval(port, JS)
        if not result:
            print("  （无结果或页面未找到）")
            continue
        items = json.loads(result)
        if not items:
            print("  ❌ 未找到任何疑似停止按钮")
        for it in items:
            print(f"  · {it['tag']:12}  cls={it['cls'][:40]:40}  aria={it['aria'][:30]:30}  text={it['text'][:20]}")
    except Exception as e:
        print(f"  ❌ 异常：{e}")
    print()