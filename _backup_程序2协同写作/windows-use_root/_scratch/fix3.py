import os, io

R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"

def fix(fp, reps):
    if not os.path.exists(fp):
        print("跳过:", fp); return
    t = open(fp, encoding="utf-8", errors="ignore").read()
    t2 = t
    for a, b in reps: t2 = t2.replace(a, b)
    if t2 != t:
        open(fp, "w", encoding="utf-8", newline="\n").write(t2)
        print("改:", fp.replace(R, ""))

# 1. 自动化 README
fix(os.path.join(R, "自动化", "README_自动化流程.md"), [
    ("匿名盲审→QUEST分批融合→自检查错",
     "匿名盲审→融合官分批融合→自检查错"),
    ("- `QUEST`：唯一**融合官**（QUEST），融合只产出新文档、不改原文件，放 `_融合产物/`。",
     "- **融合官**：唯一，融合只产出新文档、不改原文件，放 `_融合产物/`。"),
    ("驱动 QUEST按 `B_融合任务书.md` **分批**产出（`融合/` 内",
     "驱动融合官按 `B_融合任务书.md` **分批**产出（`_融合产物/` 内"),
])

# 2. 融合指令末步汇总
fix(os.path.join(R, "资料", "指令", "融合轮", "融合_末步_汇总.txt"), [
    (r"QUEST\融合\规划轮\\", r"_融合产物\规划轮\\"),
    (r"QUEST\融合\融合_", r"_融合产物\融合_"),
])

# 3. 资料库 章纲轮
fix(os.path.join(R, "资料", "资料库", "章纲轮_统一启动提示词.md"), [
    ("`融合/融合_总稿_规划轮.md`", "`_融合产物/融合_总稿_规划轮.md`"),
    ("上轮 QUEST 融合出的", "上轮融合官融合出的"),
])

# 4. 资料库 正文轮/润色轮（把 "QUEST" 名字去掉，只留路径）
for fn in ["正文轮_统一启动提示词.md", "润色轮_统一启动提示词.md"]:
    fix(os.path.join(R, "资料", "资料库", fn), [
        ("上轮 QUEST 融合出的", "上轮融合官融合出的"),
        ("由 QUEST 产出", "由融合官产出"),
    ])

# 5. 再扫一遍真正的问题
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
            # 只报"融合官"和"QUEST"同现的
            if "融合官" in line and "QUEST" in line:
                hits.append((fp.replace(R,""), i, line.strip()[:130]))
            # 或 "QUEST\融合" / "QUEST/融合"
            elif "QUEST\\融合" in line or "QUEST/融合" in line:
                hits.append((fp.replace(R,""), i, line.strip()[:130]))

print(f"残留 {len(hits)} 处：")
for rel, i, line in hits:
    print(f"  {rel} L{i}")
    print(f"     {line}")