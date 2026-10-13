import sys, json
from pathlib import Path

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab

port = 9223
# 两个 iframe 的 URL 关键词
iframe_kws = [
    "0u5u1gqchrl239fn0nq5ms27e4i6kon3c0lomsvf51fncequasuj",
    "1g90s0learct7flb452d95a8lkk25t6g1b0ttgtk0hm39jjt4112",
]

for kw in iframe_kws:
    print(f"\n{'='*70}")
    print(f"测试 iframe: {kw[:50]}...")
    print('='*70)
    try:
        tab = CDPTab(port, kw=kw)
        # 查所有可能的输入框
        result = tab.js("""
        (() => {
            const out = {
                textareas: [],
                editables: [],
                textbox_roles: [],
                all_placeholders: []
            };
            document.querySelectorAll('textarea').forEach((el, i) => {
                const r = el.getBoundingClientRect();
                out.textareas.push({
                    i,
                    cls: (el.className||'').slice(0, 80),
                    ph: el.placeholder || '',
                    visible: r.width > 0 && r.height > 0,
                    w: Math.round(r.width), h: Math.round(r.height)
                });
            });
            document.querySelectorAll('[contenteditable="true"]').forEach((el, i) => {
                const r = el.getBoundingClientRect();
                out.editables.push({
                    i,
                    cls: (el.className||'').slice(0, 80),
                    ph: el.getAttribute('data-placeholder') || el.getAttribute('placeholder') || '',
                    visible: r.width > 0 && r.height > 0,
                    w: Math.round(r.width), h: Math.round(r.height)
                });
            });
            document.querySelectorAll('[role="textbox"]').forEach((el, i) => {
                const r = el.getBoundingClientRect();
                out.textbox_roles.push({
                    i,
                    cls: (el.className||'').slice(0, 80),
                    aria: el.getAttribute('aria-label') || '',
                    visible: r.width > 0 && r.height > 0,
                    w: Math.round(r.width), h: Math.round(r.height)
                });
            });
            // 抓页面里所有含"提问/输入/发送/message/chat"的元素
            const body = document.body?.innerText || '';
            out.bodySnippet = body.slice(0, 500);
            return JSON.stringify(out);
        })()
        """)
        data = json.loads(result) if isinstance(result, str) else result
        print(f"  textareas: {len(data['textareas'])} 个")
        for t in data['textareas']:
            print(f"    [{t['i']}] cls={t['cls']!r} ph={t['ph']!r} vis={t['visible']} {t['w']}x{t['h']}")
        print(f"  editables: {len(data['editables'])} 个")
        for t in data['editables']:
            print(f"    [{t['i']}] cls={t['cls']!r} ph={t['ph']!r} vis={t['visible']} {t['w']}x{t['h']}")
        print(f"  textbox_roles: {len(data['textbox_roles'])} 个")
        for t in data['textbox_roles']:
            print(f"    [{t['i']}] cls={t['cls']!r} aria={t['aria']!r} vis={t['visible']} {t['w']}x{t['h']}")
        print(f"  body 前 200 字：{data.get('bodySnippet','')[:200]!r}")
    except Exception as e:
        print(f"  ❌ 失败：{e}")
