import os, re

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
        # 找含"融合官"或"QUEST"做融合的
        if ("融合官" in t) or ("QUEST" in t and "融合" in t):
            rel = fp.replace(R, "")
            # 分别统计
            n_guan = t.count("融合官")
            n_quest = t.count("QUEST")
            # 定位每处提到"融合官...QUEST"
            patterns = [
                "融合官：QUEST", "融合官 QUEST", "融合官（QUEST", "QUEST（QUEST",
                "QUEST 做融合", "QUEST做融合", "融合官（QUEST / QUEST）",
                "融合官（QUEST）", "由 QUEST", "交给 QUEST", "QUEST 主笔",
            ]
            found = [p for p in patterns if p in t]
            if found or n_guan:
                hits.append((rel, n_guan, n_quest, found))

print(f"共 {len(hits)} 个文件涉及")
for rel, ng, nq, found in sorted(hits):
    print(f"\n{rel}")
    print(f"   融合官×{ng}  QUEST×{nq}")
    if found: print(f"   命中: {found}")