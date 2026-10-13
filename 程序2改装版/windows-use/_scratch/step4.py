import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
hits = []
for dp, _, fs in os.walk(R):
    if "_融合产物" in dp: continue
    for fn in fs:
        if not (fn.endswith(".md") or fn.endswith(".txt")): continue
        fp = os.path.join(dp, fn)
        try: t = open(fp, encoding="utf-8", errors="ignore").read()
        except: continue
        for i, line in enumerate(t.splitlines(), 1):
            if "QUEST" in line and "融合" in line:
                hits.append((fp.replace(R,""), i, line.strip()[:140]))

print(f"共 {len(hits)} 处")
for rel, i, line in hits:
    print(f"{rel}  L{i}")
    print(f"   {line}")