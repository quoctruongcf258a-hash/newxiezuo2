fp = r"C:\mai\multi-ai-pipeline\windows-use\mix_send.py"
with open(fp, "r", encoding="utf-8") as f:
    t = f.read()

# CDP_APPS 里加 TraeWork 已有 9225
# 把 Qianwen 从 PYA_APPS 挪到 CDP_APPS，指向 9225

# 1. 从 PYA_APPS 删掉 Qianwen
t = t.replace('    "Qianwen":   "qianwen",\n', '')

# 2. CDP_APPS 里加 Qianwen 指向 9225
if '"Qianwen":' not in t.split("PYA_APPS")[0]:
    t = t.replace(
        '"TraeWork":  (9225, ""),',
        '"TraeWork":  (9225, ""),\n    "Qianwen":   (9225, ""),   # TraeWork 顶替千问'
    )

with open(fp, "w", encoding="utf-8") as f:
    f.write(t)
print("✅ Qianwen → 9225（TraeWork）")

# 验证
with open(fp, "r", encoding="utf-8") as f:
    content = f.read()
print("\n=== CDP_APPS ===")
in_cdp = False
for line in content.splitlines():
    if "CDP_APPS = {" in line: in_cdp = True; continue
    if in_cdp:
        if "}" in line: break
        print("  " + line.strip())
print("\n=== PYA_APPS ===")
in_pya = False
for line in content.splitlines():
    if "PYA_APPS = {" in line: in_pya = True; continue
    if in_pya:
        if "}" in line: break
        print("  " + line.strip())
