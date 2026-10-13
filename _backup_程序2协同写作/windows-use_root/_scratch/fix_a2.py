import os, re
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

# 1. 融合总稿去署名
F = os.path.join(R, "_融合产物", "融合_总稿_规划轮.md")
t = open(F, encoding="utf-8").read()
t = t.replace("> **融合官**：ZCode（选手6）。", "> ")
t = re.sub(r"（ZCode[^）]*）", "", t)
t = re.sub(r"\*\*融合官\*\*：ZCode[^\n]*\n", "", t)
open(F, "w", encoding="utf-8", newline="\n").write(t)
print("改: 融合_总稿_规划轮.md")

# 2. 所有 A2 任务书
for p in P:
    fp = os.path.join(R, p, "A2_章纲任务书.md")
    if not os.path.exists(fp): continue
    t = open(fp, encoding="utf-8").read()
    t2 = t
    t2 = t2.replace("（`融合/融合_总稿_规划轮.md`，由 QUEST 产出）", "（`_融合产物/融合_总稿_规划轮.md`）")
    t2 = t2.replace("（`融合/融合_总稿_规划轮.md`，由融合官产出）", "（`_融合产物/融合_总稿_规划轮.md`）")
    t2 = t2.replace("`融合/融合_总稿_规划轮.md`", "`_融合产物/融合_总稿_规划轮.md`")
    t2 = t2.replace("先等规划轮完成、QUEST 融合后再开工", "先等规划轮完成、融合后再开工")
    t2 = t2.replace("由 QUEST 产出", "由融合官产出")
    t2 = t2.replace("QUEST 融合", "融合官融合")
    if t2 != t:
        open(fp, "w", encoding="utf-8", newline="\n").write(t2)
        print(f"改: {p}\\A2_章纲任务书.md")

# 3. 复扫
print("\n=== 复扫 ===")
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
                hits.append((fp.replace(R,""), i, line.strip()[:130]))
            elif "ZCode" in line and "融合官" in line:
                hits.append((fp.replace(R,""), i, "[ZCode官] " + line.strip()[:130]))
if hits:
    for rel, i, line in hits:
        print(f"  {rel} L{i}: {line}")
else:
    print("✅ 0 残留")
