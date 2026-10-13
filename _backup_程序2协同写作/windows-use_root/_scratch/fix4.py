import os

R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","TRAE","WorkBuddy","ZCode"]

def fix(fp, reps):
    if not os.path.exists(fp): return False
    t = open(fp, encoding="utf-8", errors="ignore").read()
    t2 = t
    for a, b in reps: t2 = t2.replace(a, b)
    if t2 != t:
        open(fp, "w", encoding="utf-8", newline="\n").write(t2)
        print("改:", fp.replace(R, ""))
        return True
    return False

# 1. 所有选手 A3/A4/正文轮提示词：QUEST/融合/ 和 QUEST\\融合\\
for p in P:
    for fn in ["A3_正文任务书.md", "A4_润色任务书.md", "正文轮任务提示词.txt"]:
        fix(os.path.join(R, p, fn), [
            ("QUEST/融合/", "_融合产物/"),
            ("QUEST\\融合\\", "_融合产物\\"),
        ])

# 2. 融合_末步_汇总.txt：用正则替换所有 QUEST\融合\
fp = os.path.join(R, "资料", "指令", "融合轮", "融合_末步_汇总.txt")
if os.path.exists(fp):
    t = open(fp, encoding="utf-8").read()
    t2 = t.replace("QUEST\\融合\\", "_融合产物\\")
    t2 = t2.replace("QUEST/融合/", "_融合产物/")
    if t2 != t:
        open(fp, "w", encoding="utf-8", newline="\n").write(t2)
        print("改: 融合_末步_汇总.txt")

# 3. 资料库三个提示词
for fn in ["正文轮_统一启动提示词.md", "润色轮_统一启动提示词.md", "章纲轮_统一启动提示词.md"]:
    fix(os.path.join(R, "资料", "资料库", fn), [
        ("QUEST/融合/", "_融合产物/"),
        ("`融合/融合_总稿_规划轮.md`", "`_融合产物/融合_总稿_规划轮.md`"),
        ("上轮 QUEST 融合出的", "上轮融合官融合出的"),
        ("由 QUEST 产出", "由融合官产出"),
    ])

# 4. 复扫
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
            if ("QUEST\\融合" in line or "QUEST/融合" in line
                or ("融合官" in line and "QUEST" in line)):
                hits.append((fp.replace(R,""), i, line.strip()[:130]))

if hits:
    print(f"残留 {len(hits)} 处：")
    for rel, i, line in hits:
        print(f"  {rel} L{i}")
        print(f"     {line}")
else:
    print("✅ 0 残留，全部清完")