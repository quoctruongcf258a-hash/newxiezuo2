# diag_stop_btn.py — 诊断各 AI 的「停止」按钮特征
import sys, time
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab, _lookup

for ai in ["QUEST", "WorkBuddy", "Doubao", "gemini"]:
    print(f"===== {ai} =====")
    info = _lookup(ai)
    if not info or not info[0]:
        print("  无端口")
        continue
    port, kw = info
    try:
        tab = CDPTab(port, kw)
        # 列出所有含 停止/Stop 的按钮
        btns = tab.js("""
        (() => {
            const out = [];
            for (const b of document.querySelectorAll('button, [role="button"], [class*="stop"], [class*="Stop"]')) {
                const r = b.getBoundingClientRect();
                if (r.width <= 0 || r.height <= 0) continue;
                const aria = (b.getAttribute('aria-label')||'').trim();
                const cls = (b.className||'').toString().slice(0,80);
                const title = (b.getAttribute('title')||'').trim();
                out.push({
                    tag: b.tagName,
                    aria: aria.slice(0,40),
                    cls: cls,
                    title: title.slice(0,40),
                    x: Math.round(r.x + r.width/2),
                    y: Math.round(r.y + r.height/2),
                    w: Math.round(r.width),
                    h: Math.round(r.height)
                });
            }
            return out;
        })()
        """)
        print(f"  含 stop 关键字按钮 {len(btns)} 个：")
        for b in btns:
            print(f"    tag={b['tag']}  aria={b['aria']!r}  cls={b['cls']!r}  title={b['title']!r}")
            print(f"        ({b['x']},{b['y']})  {b['w']}x{b['h']}")
    except Exception as e:
        print(f"  失败: {e}")
    print()