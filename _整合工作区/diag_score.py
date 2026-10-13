import sys
import json
import urllib.request
import websocket

PORT = 9231

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

# 与 _SCORE_JS 相同的打分逻辑 + 明细
JS = r"""
(() => {
  const sels = 'textarea, [contenteditable="true"], [role="textbox"], input[type="text"]';
  const out = [];
  for (const el of document.querySelectorAll(sels)) {
    const r = el.getBoundingClientRect();
    const st = getComputedStyle(el);
    const meta = [el.getAttribute('placeholder'), el.getAttribute('aria-label'),
                    el.getAttribute('role'), el.getAttribute('name')].filter(Boolean).join(' ');
    const detail = [];
    let score = 0;
    const area = r.width * r.height;
    score += area;
    detail.push('面积 +' + Math.round(area));

    if (el.tagName === 'TEXTAREA' || el.getAttribute('contenteditable') === 'true') {
      score += 5000000; detail.push('textarea/CE +5M');
    } else {
      score -= 5000000; detail.push('非CE -5M');
    }

    if (/链接|网址|网络地址|粘贴|url|link|搜索|search|find/i.test(meta)) {
      score -= 10000000; detail.push('非聊天 -10M');
    }

    if (/提问|问题|发送消息|消息|对话|ask|message|prompt|send|chat/i.test(meta)) {
      score += 5000000; detail.push('聊天 +5M');
    }

    if (el.getAttribute('data-slate-editor') === 'true'
        || el.querySelector('[data-slate-editor=true]')) {
      score += 100000000; detail.push('Slate +100M');
    }

    if (el.getAttribute('role') === 'textbox') {
      score += 20000000; detail.push('role=textbox +20M');
    }

    const cls = (el.className || '').toString();
    if (/root-editable|file-edit|code-editor|monaco|editor-container/i.test(cls)) {
      score -= 100000000; detail.push('文件编辑器 -100M');
    }

    out.push({
      tag: el.tagName,
      cls: cls.slice(0, 80),
      rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
      inViewport: r.y >= 0 && r.y < window.innerHeight && r.x >= 0 && r.x < window.innerWidth,
      meta: meta.slice(0, 60),
      score: score,
      detail: detail.join(' | '),
    });
  }
  out.sort((a, b) => b.score - a.score);
  return JSON.stringify(out);
})()
"""

for t in list_tabs(PORT):
    if t.get("type") != "page": continue
    url = t.get("url","")
    if "doubao-chat" not in url and "doubao-launcher" not in url: continue
    print(f"=== {t.get('title','')[:40]}  {url[:60]} ===")
    try:
        r = cdp_eval(t["webSocketDebuggerUrl"], JS)
        items = json.loads(r) if r else []
        for it in items:
            flag = " ✅" if it['inViewport'] else " ❌屏幕外"
            print(f"\n  [{it['score']:>12}]  {it['tag']}  {flag}")
            print(f"     rect={it['rect']}")
            print(f"     cls={it['cls']}")
            print(f"     meta={it['meta']}")
            print(f"     明细: {it['detail']}")
    except Exception as e:
        print(f"  异常：{e}")
    print()
