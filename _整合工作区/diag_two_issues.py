import sys, json
from pathlib import Path
from urllib.request import urlopen

# ── 问题 1：tasks.py 里 FILE_MODE_AIS 是什么 ──
print("=" * 70)
print("① tasks.py 的 FILE_MODE_AIS")
print("=" * 70)
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
try:
    import tasks
    print(f"  {tasks.FILE_MODE_AIS}")
    print(f"  codebuddy 在内：{'✅' if 'codebuddy' in tasks.FILE_MODE_AIS else '❌'}")
    print(f"  tasks.py 路径：{tasks.__file__}")
except Exception as e:
    print(f"  ❌ {e}")

# ── 问题 2：CodeBuddy 的 iframe 里有没有聊天框 ──
print()
print("=" * 70)
print("② CodeBuddy 每个 iframe 里的输入框")
print("=" * 70)

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CDPTab

port = 9223
try:
    with urlopen(f"http://127.0.0.1:{port}/json", timeout=3) as f:
        targets = json.load(f)
except Exception as e:
    print(f"❌ 连不上：{e}")
    raise SystemExit()

for t in targets:
    if t.get("type") != "iframe":
        continue
    ws = t.get("webSocketDebuggerUrl", "")
    if not ws:
        continue
    print(f"\n[iframe] {t.get('url', '')[:100]}")
    try:
        # 直接用 ws url 建立连接太复杂，用 CDPTab 传 id
        tid = t.get("id")
        tab = CDPTab(port, kw="", target_id=tid) if "target_id" in CDPTab.__init__.__code__.co_varnames else None
        if tab is None:
            # 尝试用 kw 匹配
            print("  ⚠ CDPTab 不支持直接传 target_id，跳过（下一步手动处理）")
            continue
        result = tab.js("""
        (() => {
            const out = [];
            document.querySelectorAll('textarea, [contenteditable="true"], [role="textbox"]').forEach((el, i) => {
                const r = el.getBoundingClientRect();
                if (r.width <= 0 || r.height <= 0) return;
                out.push({
                    tag: el.tagName.toLowerCase(),
                    cls: el.className?.toString().slice(0, 60) || '',
                    ph: el.placeholder || el.getAttribute('data-placeholder') || el.getAttribute('aria-label') || '',
                    w: Math.round(r.width),
                    h: Math.round(r.height),
                });
            });
            return JSON.stringify(out, null, 2);
        })()
        """)
        print(result)
    except Exception as e:
        print(f"  查询失败：{e}")
