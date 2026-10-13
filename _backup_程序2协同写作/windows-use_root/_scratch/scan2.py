import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
hits = []
for dirpath, _, files in os.walk(R):
    for fn in files:
        if not (fn.endswith(".md") or fn.endswith(".txt")): continue
        fp = os.path.join(dirpath, fn)
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                t = f.read()
        except: continue
        if "融合官" in t and "QUEST" in t:
            rel = fp.replace(R, "")
            # 抓含 QUEST 和 融合官 的行
            for line in t.splitlines():
                if "融合官" in line and "QUEST" in line:
                    hits.append((rel, line.strip()[:120]))

print(f"共 {len(hits)} 处")
for rel, line in hits:
    print(f"\n{rel}")
    print(f"   {line}")