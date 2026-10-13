# find_green_btn.py — 精确找出 QUEST 右下角绿色发送按钮
import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab

tab = CDPTab(9224)
print("页面:", tab.title[:100])
print()

btns = tab.js("""
(() => {
    const out = [];
    for (const b of document.querySelectorAll('button, [role="button"], svg, [class*="send" i], [class*="Send"]')) {
        const r = b.getBoundingClientRect();
        if (r.width <= 0 || r.height <= 0) continue;
        const x = Math.round(r.x + r.width / 2);
        const y = Math.round(r.y + r.height / 2);
        if (x < 400 || y < 350) continue;
        let bg = '';
        try { bg = getComputedStyle(b).backgroundColor; } catch(e) {}
        out.push({
            tag: b.tagName,
            aria: b.getAttribute('aria-label') || '',
            title: b.getAttribute('title') || '',
            cls: (b.className || '').toString().slice(0, 80),
            bg: bg,
            dis: !!b.disabled,
            x: x, y: y,
            w: Math.round(r.width), h: Math.round(r.height)
        });
    }
    return out;
})()
""")

print(f"找到 {len(btns)} 个候选（右下角）：")
for i, b in enumerate(btns):
    print(f"[{i}] tag={b['tag']}  ({b['x']},{b['y']})  {b['w']}x{b['h']}")
    print(f"    aria={b['aria']!r}  title={b['title']!r}")
    print(f"    cls={b['cls']!r}")
    print(f"    bg={b['bg']!r}  disabled={b['dis']}")
    print()