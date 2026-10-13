fp = r"C:\mai\multi-ai-pipeline\windows-use\mix_send.py"
with open(fp, "r", encoding="utf-8") as f:
    t = f.read()

# 1. CDP_APPS 加 Qianwen（指向 9225）
if '"Qianwen":   (9225' not in t:
    t = t.replace(
        '"TraeWork":  (9225, ""),',
        '"TraeWork":  (9225, ""),\n    "Qianwen":   (9225, ""),   # TraeWork 顶替千问'
    )

# 2. PYA_APPS 删掉 Qianwen
t = t.replace('    "Qianwen":   "qianwen",\n', '')

with open(fp, "w", encoding="utf-8") as f:
    f.write(t)

print("=== 改后 CDP_APPS ===")
in_cdp = False
for line in t.splitlines():
    if "CDP_APPS = {" in line: in_cdp = True; continue
    if in_cdp:
        if "}" in line: break
        print("  " + line.strip())

print("\n=== 改后 PYA_APPS ===")
in_pya = False
for line in t.splitlines():
    if "PYA_APPS = {" in line: in_pya = True; continue
    if in_pya:
        if "}" in line: break
        print("  " + line.strip())
