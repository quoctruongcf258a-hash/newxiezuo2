import sys, json
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab

port = 9223

# 抓所有 target（page + iframe）
with urlopen(f"http://127.0.0.1:{port}/json", timeout=3) as f:
    targets = json.load(f)

# 只处理 page 和 iframe
targets = [t for t in targets if t.get("type") in ("page", "iframe")]

for t in targets:
    tid = t.get("id")
    url = t.get("url", "")
    print(f"\n{'='*70}")
    print(f"target: {url[:80]}")
    print('='*70)
    # CDPTab 用 url_kw 匹配，这里传 target 特有片段
    # 尝试用 url 中一段唯一字符串
    # 简化：直接用 CDPTab(port, kw) 看看能不能匹配到
    # 找 kw：url 里的 hash 部分
    kw = ""
    if "vscode-webview://" in url:
        # 提取 hash
        parts = url.split("vscode-webview://")
        if len(parts) > 1:
            kw = parts[1].split("/")[0]
    try:
        tab = CDPTab(port, kw=kw)
        result = tab.js("""
        (() => {
            const out = {found: []};
            // 找所有带"提问"或"输入"placeholder 的
            const all = document.querySelectorAll('textarea, [contenteditable="true"], [role="textbox"], input');
            all.forEach((el, i) => {
                const r = el.getBoundingClientRect();
                if (r.width <= 0 || r.height <= 0) return;
                const ph = el.placeholder || el.getAttribute('data-placeholder') || el.getAttribute('aria-label') || '';
                const cls = (el.className||'').toString().slice(0, 100);
                out.found.push({
                    tag: el.tagName.toLowerCase(),
                    cls: cls,
                    ph: ph,
                    w: Math.round(r.width),
                    h: Math.round(r.height),
                    top: Math.round(r.top),
                    left: Math.round(r.left)
                });
            });
            return JSON.stringify(out);
        })()
        """)
        data = json.loads(result) if isinstance(result, str) else result
        for f_item in data.get("found", []):
            print(f"  [{f_item['tag']}] cls={f_item['cls']!r}")
            print(f"      ph={f_item['ph']!r}  size={f_item['w']}x{f_item['h']}  pos=({f_item['left']},{f_item['top']})")
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}")

# 额外：直接暴力搜整页面所有含"提问"文本的元素
print(f"\n{'='*70}")
print("暴力搜索：所有含「提问」文本的元素")
print('='*70)
try:
    tab_main = CDPTab(port, "")
    result = tab_main.js("""
    (() => {
        const out = [];
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node;
        while (node = walker.nextNode()) {
            if ((node.textContent || '').includes('提问')) {
                const el = node.parentElement;
                const r = el.getBoundingClientRect();
                out.push({
                    tag: el.tagName.toLowerCase(),
                    cls: (el.className||'').toString().slice(0, 100),
                    text: node.textContent.slice(0, 100),
                    w: Math.round(r.width),
                    h: Math.round(r.height),
                });
            }
        }
        return JSON.stringify(out);
    })()
    """)
    data = json.loads(result) if isinstance(result, str) else result
    for item in data:
        print(f"  [{item['tag']}] cls={item['cls']!r}")
        print(f"      text={item['text']!r}  size={item['w']}x{item['h']}")
except Exception as e:
    print(f"  ❌ {type(e).__name__}: {e}")
