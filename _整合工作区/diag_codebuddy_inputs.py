import sys, json
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")

# 直接用 CDP 查 CodeBuddy 页面
from mix_send import CDPTab, _lookup

info = _lookup("CodeBuddy")
if not info:
    print("❌ 找不到 CodeBuddy 配置")
    sys.exit()

port, kw = info
print(f"CodeBuddy: port={port}, kw={kw}")

tab = CDPTab(port, kw)

# 检查页面里的所有输入框
result = tab.js("""
(() => {
    const out = [];
    // textarea
    document.querySelectorAll('textarea').forEach((el, i) => {
        const r = el.getBoundingClientRect();
        out.push({
            tag: 'textarea',
            idx: i,
            cls: el.className?.toString().slice(0, 80) || '',
            id: el.id || '',
            ph: el.placeholder || '',
            visible: r.width > 0 && r.height > 0,
            w: Math.round(r.width),
            h: Math.round(r.height),
            top: Math.round(r.top),
        });
    });
    // contenteditable
    document.querySelectorAll('[contenteditable="true"]').forEach((el, i) => {
        const r = el.getBoundingClientRect();
        out.push({
            tag: 'contenteditable',
            idx: i,
            cls: el.className?.toString().slice(0, 80) || '',
            id: el.id || '',
            ph: el.getAttribute('data-placeholder') || el.getAttribute('placeholder') || '',
            visible: r.width > 0 && r.height > 0,
            w: Math.round(r.width),
            h: Math.round(r.height),
            top: Math.round(r.top),
        });
    });
    // role=textbox
    document.querySelectorAll('[role="textbox"]').forEach((el, i) => {
        const r = el.getBoundingClientRect();
        out.push({
            tag: 'role=textbox',
            idx: i,
            cls: el.className?.toString().slice(0, 80) || '',
            id: el.id || '',
            ph: el.getAttribute('aria-label') || '',
            visible: r.width > 0 && r.height > 0,
            w: Math.round(r.width),
            h: Math.round(r.height),
            top: Math.round(r.top),
        });
    });
    return JSON.stringify(out, null, 2);
})()
""")

print("=" * 70)
print("CodeBuddy 页面所有输入框")
print("=" * 70)
try:
    data = json.loads(result) if isinstance(result, str) else result
    for item in data:
        print(f"\n[{item['tag']}#{item['idx']}]")
        print(f"  class: {item['cls']}")
        print(f"  id: {item['id']}")
        print(f"  占位: {item['ph']}")
        print(f"  可见: {item['visible']}  尺寸: {item['w']}x{item['h']}  top: {item['top']}")
except Exception as e:
    print(f"解析失败：{e}")
    print(f"原始：{result}")
