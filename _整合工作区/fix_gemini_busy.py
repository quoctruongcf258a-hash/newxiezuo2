# fix_gemini_busy.py — 给 gemini 加专用忙闲检测
import shutil
from pathlib import Path

MIX = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
text = MIX.read_text(encoding="utf-8")

OLD = '''    port, kw = info
    try:
        tab = CDPTab(port, kw)
        return bool(tab.js("""
        (() => {
            // 1. 找「停止」按钮（几乎所有 AI 生成时都显示）
            for (const b of document.querySelectorAll('button, [role="button"]')) {'''

NEW = '''    port, kw = info
    key = ai.lower()
    try:
        tab = CDPTab(port, kw)
        # gemini (Antigravity) 专用：忙时按钮 aria 含 "Cancel"
        if key == "gemini":
            return bool(tab.js("""
            (() => {
                for (const b of document.querySelectorAll('button, [role="button"]')) {
                    const a = (b.getAttribute('aria-label')||'').toLowerCase();
                    const r = b.getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) continue;
                    if (a.includes('cancel')) return true;
                }
                return false;
            })()
            """))
        return bool(tab.js("""
        (() => {
            // 1. 找「停止」按钮（几乎所有 AI 生成时都显示）
            for (const b of document.querySelectorAll('button, [role="button"]')) {'''

if 'gemini (Antigravity) 专用' in text:
    print("已改过")
elif OLD not in text:
    print("✗ 找不到 is_ai_busy 锚点")
else:
    bak = MIX.with_suffix(".py.bak_geminibusy")
    if not bak.exists():
        shutil.copy(MIX, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    MIX.write_text(text, encoding="utf-8")
    print("✔ gemini 专用忙闲检测已加")