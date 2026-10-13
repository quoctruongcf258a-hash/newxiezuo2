# dump_inputs.py — 列出 WorkBuddy 页面上所有输入框候选（含打分）
import sys, json, urllib.request
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab, _SCORE_JS

tab = CDPTab(9227)

# 1) 列出所有候选
js = """
(() => {
  const sels = 'textarea, [contenteditable="true"], [role="textbox"], input[type="text"]';
  const out = [];
  for (const el of document.querySelectorAll(sels)) {
    const r = el.getBoundingClientRect();
    const st = getComputedStyle(el);
    if (r.width <= 0 || r.height <= 0) continue;
    if (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0' || el.offsetParent === null) continue;
    const meta = [el.getAttribute('placeholder'), el.getAttribute('aria-label'),
                  el.getAttribute('role'), el.getAttribute('name')].filter(Boolean).join(' ');
    out.push({
      tag: el.tagName,
      cls: (el.className||'').toString().slice(0, 80),
      area: Math.round(r.width * r.height),
      placeholder: el.getAttribute('placeholder') || '',
      aria: el.getAttribute('aria-label') || '',
      role: el.getAttribute('role') || '',
      slate: el.getAttribute('data-slate-editor') === 'true',
      meta: meta.slice(0, 100),
      x: Math.round(r.x + r.width/2),
      y: Math.round(r.y + r.height/2)
    });
  }
  return out;
})()
"""
result = tab.js(js)
print(f"共 {len(result)} 个候选输入框：\n")
for i, el in enumerate(result):
    print(f"[{i}] tag={el['tag']}  cls={el['cls']}")
    print(f"    area={el['area']}  slate={el['slate']}  x,y=({el['x']},{el['y']})")
    print(f"    placeholder={el['placeholder'][:50]!r}")
    print(f"    aria={el['aria'][:50]!r}  role={el['role']!r}")
    print()