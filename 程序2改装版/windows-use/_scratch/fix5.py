fp = r"C:\mai\multi-ai-pipeline\windows-use\mix_send.py"
with open(fp, "r", encoding="utf-8") as f:
    t = f.read()

old = '''        left = self.js("""
        (() => {
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return -1;
            return el.value !== undefined ? el.value.length : el.textContent.length;
        })()
        """)
        return f"剩余={left}"'''

new = '''        left = self.js("""
        (() => {
            const el = document.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
            if (!el) return -1;
            const slate = el.querySelector('[data-slate-string="true"]');
            if (slate) return slate.textContent.length;
            return el.value !== undefined ? el.value.length : (el.textContent || "").trim().length;
        })()
        """)
        return f"剩余={left}"'''

if old in t:
    t = t.replace(old, new)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(t)
    print("✅ 已改")
else:
    print("❌ 没找到")
