# diag_gemini_busy.py — 专门诊断 gemini 的忙闲特征
import sys, time
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab, _lookup

info = _lookup("gemini")
print(f"gemini 端口: {info}")
port, kw = info

for i in range(6):
    print(f"\n========== 第 {i+1} 次探测（间隔 5 秒）==========")
    try:
        tab = CDPTab(port, kw)
        # 1. 抓所有可见按钮
        btns = tab.js("""
        (() => {
            const out = [];
            for (const b of document.querySelectorAll('button, [role="button"]')) {
                const r = b.getBoundingClientRect();
                if (r.width <= 0 || r.height <= 0) continue;
                const a = (b.getAttribute('aria-label')||'').trim();
                const c = (b.className||'').toString().slice(0, 60);
                const txt = (b.textContent||'').trim().slice(0,20);
                // 只挑右下角 + 有意义的（位置 x>500）
                if (r.x + r.width/2 > 500 && r.y + r.height/2 > 300) {
                    out.push({a, c, txt, x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)});
                }
            }
            return out;
        })()
        """)
        print(f"右下角按钮 {len(btns)} 个：")
        for b in btns:
            print(f"  aria={b['a']!r}  txt={b['txt']!r}  cls={b['c']!r}  ({b['x']},{b['y']})")
        # 2. 页面文字特征
        txt = tab.js("(document.body.innerText||'').slice(0, 300)")
        print(f"页面文字开头：{txt[:200]!r}")
    except Exception as e:
        print(f"失败: {e}")
    time.sleep(5)