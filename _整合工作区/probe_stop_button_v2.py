import json
import sys
import urllib.request
import websocket
from pathlib import Path

TODAY = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\today.json")
data = json.loads(TODAY.read_text(encoding="utf-8"))


def list_tabs(port, timeout=5):
    r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=timeout)
    return json.loads(r.read().decode("utf-8"))


def cdp_eval(ws_url, js, timeout=8):
    ws = websocket.create_connection(ws_url, timeout=timeout)
    try:
        ws.send(json.dumps({
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {"expression": js, "returnByValue": True, "awaitPromise": False},
        }))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == 1:
                return resp.get("result", {}).get("result", {}).get("value")
    finally:
        ws.close()


# 新版 JS：穿透 Shadow DOM + 抓所有可见按钮
JS = r"""
(() => {
  const out = [];

  function walk(root, depth) {
    if (!root || depth > 6) return;
    let nodes;
    try { nodes = root.querySelectorAll('*'); } catch (e) { return; }
    for (const el of nodes) {
      // 穿透 shadowRoot
      if (el.shadowRoot) walk(el.shadowRoot, depth + 1);
      // 只看按钮类元素
      const tag = el.tagName;
      const role = el.getAttribute('role') || '';
      const cls = (el.className || '').toString();
      const isBtn = tag === 'BUTTON' || role === 'button' ||
                    cls.includes('stop') || cls.includes('Stop') ||
                    cls.includes('cancel') || cls.includes('Cancel');
      if (!isBtn) continue;

      const r = el.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) continue;
      const st = getComputedStyle(el);
      if (st.display === 'none' || st.visibility === 'hidden') continue;

      out.push({
        tag: tag,
        role: role,
        cls: cls.slice(0, 80),
        id: el.id || '',
        aria: el.getAttribute('aria-label') || '',
        title: el.getAttribute('title') || '',
        testid: el.getAttribute('data-testid') || '',
        dataIcon: el.getAttribute('data-icon') || '',
        text: (el.textContent || '').trim().slice(0, 40),
        rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
      });
    }
  }

  walk(document, 0);
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
        tabs = list_tabs(port)
        pages = [t for t in tabs if t.get("type") == "page" and not t.get("url", "").startswith("devtools")]
        if not pages:
            print("  ❌ 没有可用的 page tab")
            print()
            continue

        # 打印所有 page tab，看有几个
        print(f"  共 {len(pages)} 个 page tab：")
        for i, p in enumerate(pages):
            print(f"    [{i}] {p.get('title', '')[:40]}  url={p.get('url', '')[:80]}")
        print()

        # 对每个 page tab 都抓一遍
        for i, p in enumerate(pages):
            print(f"  ── tab[{i}] {p.get('title', '')[:30]} ──")
            try:
                result = cdp_eval(p["webSocketDebuggerUrl"], JS)
                if not result:
                    print("    （无结果）")
                    continue
                items = json.loads(result)
                if not items:
                    print("    ❌ 无按钮类元素")
                    continue
                print(f"    共 {len(items)} 个按钮：")
                for it in items[:30]:   # 最多显示 30 个
                    print(f"      {it['tag']:10} role={it['role']:8} aria={it['aria'][:25]:25} "
                          f"title={it['title'][:15]:15} data-icon={it['dataIcon'][:10]:10} text={it['text'][:15]}")
                if len(items) > 30:
                    print(f"    … 还有 {len(items) - 30} 个未显示")
            except Exception as e:
                print(f"    ❌ tab[{i}] 异常：{e}")

    except Exception as e:
        print(f"  ❌ 异常：{e}")
    print()