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
        if "融合官" in t or ("融合" in t and ("QUEST" in t or "ZCode" in t)):
            rel = fp.replace(R, "")
            lines = []
            for i, line in enumerate(t.splitlines(), 1):
                if "融合官" in line:
                    lines.append((i, line.strip()[:150]))
                elif "融合" in line and ("QUEST" in line or "ZCode" in line):
                    lines.append((i, "[配合] " + line.strip()[:150]))
            if lines:
                hits.append((rel, lines))

print(f"共 {len(hits)} 个文件")
for rel, lines in sorted(hits):
    print(f"\n{'='*70}")
    print(f"{rel}")
    print('='*70)
    for i, line in lines:
        print(f"  L{i}: {line}")