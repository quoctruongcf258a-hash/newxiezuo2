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
                hits.append((fp.replace(R,""), i, line.strip()[:130]))

print(f"=== 残留 {len(hits)} 处 ===")
for rel, i, line in hits:
    print(f"  {rel}  L{i}")
    print(f"     {line}")

# 检查关键文件是否存在
print("\n=== 关键文件 ===")
for p in [r"ZCode\B_融合任务书.md", r"ZCode\00_你的输出位置.md", r"_融合产物"]:
    fp = os.path.join(R, p)
    print(f"  {'✅' if os.path.exists(fp) else '❌'} {p}")

# 看备份里有没有 B_融合任务书
bak = r"C:\Users\Administrator\Desktop\新书\火影忍者\_七人赛马备份_融合改名前"
print(f"\n备份路径存在: {os.path.exists(bak)}")
if os.path.exists(bak):
    for f in os.listdir(bak):
        print(f"   {f}")