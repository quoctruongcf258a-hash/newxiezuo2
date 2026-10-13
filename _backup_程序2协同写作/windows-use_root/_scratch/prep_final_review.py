import os, io
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"

# 检查融合总稿
F = os.path.join(R, "_融合产物", "融合_总稿_规划轮.md")
print("融合总稿:", "✅" if os.path.exists(F) else "❌", os.path.getsize(F) if os.path.exists(F) else 0)

# 合并 WorkBuddy 7 份（不含总稿）
d = os.path.join(R, "WorkBuddy", "产出", "规划轮")
OUT = os.path.join(R, "_融合产物", "_待审", "版A.md")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
chunks = []
for fn in sorted(os.listdir(d)):
    if not fn.endswith(".md"): continue
    if "总稿" in fn: continue
    with open(os.path.join(d, fn), encoding="utf-8") as f:
        t = f.read()
    chunks.append(f"\n\n{'='*70}\n## {fn}\n{'='*70}\n\n{t}")
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("".join(chunks))
print(f"版A（合并WorkBuddy）: {os.path.getsize(OUT)/1024:.1f} KB")

# 融合总稿 → 版B
OUT2 = os.path.join(R, "_融合产物", "_待审", "版B.md")
with open(F, encoding="utf-8") as f:
    t = f.read()
with io.open(OUT2, "w", encoding="utf-8") as f:
    f.write(t)
print(f"版B（融合总稿）: {os.path.getsize(OUT2)/1024:.1f} KB")