# check_tab.py — 探测 WorkBuddy 现在会选中哪个 page
import sys, json, urllib.request
from pathlib import Path

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab

port = 9227
print(f"=== 端口 {port} 下所有 page ===")
with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as f:
    pages = json.load(f)
for p in pages:
    if p.get("type") == "page":
        print(f"  title={p.get('title','')[:50]}")
        print(f"    url={p.get('url','')[:100]}")
        print()

print("=== CDPTab 最终选中 ===")
try:
    tab = CDPTab(port)
    print(f"  选中页面标题: {tab.title}")
    print(f"  ws 是否连接: {tab.ws is not None}")
    box = tab.js(
        "(() => { var s = " + __import__('mix_send')._SCORE_JS + "; "
        "if (!s.length) return null; var el = s[0].el; var r = el.getBoundingClientRect(); "
        "return {area: Math.round(r.width*r.height), "
        "slate: el.getAttribute('data-slate-editor') === 'true' || !!el.querySelector('[data-slate-editor=true]'), "
        "cls: (el.className||'').toString().slice(0,80)}; })()"
    )
    print(f"  选中的输入框: {box}")
except Exception as e:
    print(f"  失败: {e}")