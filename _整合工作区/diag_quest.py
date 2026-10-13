# diag_quest.py — 诊断 QUEST 页面的发送按钮 / 输入框剩余
import sys, json, urllib.request
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab, _LEFT_JS

tab = CDPTab(9224)
print("选中页面:", tab.title)
print()

# 1. 输入框剩余字符
left = tab.js(_LEFT_JS)
print(f"_LEFT_JS 返回: {left}")
print()

# 2. 列出所有 button / role=button 的 aria-label
btns = tab.js("""
(() => {
    const out = [];
    for (const b of document.querySelectorAll('button, [role="button"]')) {
        const r = b.getBoundingClientRect();
        if (r.width <= 0 || r.height <= 0) continue;
        out.push({
            aria: (b.getAttribute('aria-label')||'').slice(0, 40),
            title: (b.getAttribute('title')||'').slice(0, 40),
            cls: (b.className||'').toString().slice(0, 60),
            disabled: !!b.disabled,
            x: Math.round(r.x + r.width/2),
            y: Math.round(r.y + r.height/2)
        });
    }
    return out;
})()
""")
print(f"页面上共 {len(btns)} 个可见按钮：")
for i, b in enumerate(btns):
    print(f"  [{i}] aria={b['aria']!r}  title={b['title']!r}")
    print(f"      cls={b['cls']!r}  disabled={b['disabled']}  x,y=({b['x']},{b['y']})")