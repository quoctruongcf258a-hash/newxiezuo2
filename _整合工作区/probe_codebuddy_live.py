import json
import urllib.request
import websocket
import time

PORT = 9223  # CodeBuddy

def list_tabs(port):
    r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5)
    return json.loads(r.read().decode("utf-8"))

def cdp_eval(ws_url, js):
    ws = websocket.create_connection(ws_url, timeout=8)
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

# 抓所有可见按钮，不筛关键词，全量输出
JS = r"""
(() => {
  const out = [];
  function walk(root, depth) {
    if (!root || depth > 6) return;
    let nodes;
    try { nodes = root.querySelectorAll('*'); } catch (e) { return; }
    for (const el of nodes) {
      if (el.shadowRoot) walk(el.shadowRoot, depth + 1);
      const tag = el.tagName;
      const role = el.getAttribute('role') || '';
      const isBtn = tag === 'BUTTON' || role === 'button' ||
                    (el.className && (el.className.toString().includes('stop') ||
                                      el.className.toString().includes('cancel')));
      if (!isBtn) continue;
      const r = el.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) continue;
      // 只抓屏幕下半部分 + 右侧的按钮（生成按钮通常在输入框附近）
      if (r.y < window.innerHeight * 0.5) continue;
      const st = getComputedStyle(el);
      if (st.display === 'none' || st.visibility === 'hidden') continue;
      out.push({
        tag: tag,
        cls: (el.className || '').toString().slice(0, 60),
        aria: el.getAttribute('aria-label') || '',
        title: el.getAttribute('title') || '',
        text: (el.textContent || '').trim().slice(0, 30),
        rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
        html: el.outerHTML.slice(0, 200),
      });
    }
  }
  walk(document, 0);
  return JSON.stringify(out);
})()
"""

# 跑三次，间隔 3 秒，看哪些按钮在变
for round_no in range(3):
    print(f"\n{'=' * 70}")
    print(f"第 {round_no + 1} 轮（{time.strftime('%H:%M:%S')}）")
    print(f"{'=' * 70}")
    try:
        tabs = list_tabs(PORT)
        pages = [t for t in tabs if t.get("type") == "page"
                 and not t.get("url", "").startswith("devtools")]
        # 跳过 vscode-file 主界面，找聊天页
        chat_pages = [p for p in pages if "vscode-file" in p.get("url", "")]
        if not chat_pages:
            print("  没有聊天页 tab")
            continue
        # 用第一个 vscode-file 页
        for p in chat_pages[:2]:
            title = p.get("title", "")[:30]
            print(f"  ── tab: {title} ──")
            result = cdp_eval(p["webSocketDebuggerUrl"], JS)
            if not result:
                print("    （无结果）")
                continue
            items = json.loads(result)
            print(f"    共 {len(items)} 个下方按钮：")
            for it in items:
                print(f"      {it['tag']:8} cls={it['cls'][:30]:30} aria={it['aria'][:20]:20} "
                      f"title={it['title'][:12]:12} text={it['text'][:15]:15} rect={it['rect']}")
    except Exception as e:
        print(f"  异常：{e}")
    time.sleep(3)