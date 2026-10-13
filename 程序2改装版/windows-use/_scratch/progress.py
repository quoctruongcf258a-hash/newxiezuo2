import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"

print("=== 章纲轮融合产物 ===")
d = os.path.join(R, "_融合产物", "章纲轮")
if os.path.isdir(d):
    for f in sorted(os.listdir(d)):
        print(f"  {f}  ({os.path.getsize(os.path.join(d,f))} B)")
else:
    print("  (目录不存在)")

print("\n=== 章纲轮总稿 ===")
fp = os.path.join(R, "_融合产物", "融合_总稿_章纲轮.md")
if os.path.exists(fp):
    print(f"  ✅ 存在 ({os.path.getsize(fp)} B)")
else:
    print("  ❌ 不存在")

print("\n=== 章纲轮终审目录（各家评审） ===")
for p in ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]:
    d2 = os.path.join(R, p, "评审", "章纲轮终审")
    if os.path.isdir(d2):
        n = len([f for f in os.listdir(d2) if f.endswith(".md")])
        print(f"  {p:12} {n} 份")

print("\n=== 章纲轮终审汇总 ===")
d3 = os.path.join(R, "_融合产物", "章纲轮终审汇总")
if os.path.isdir(d3):
    for f in sorted(os.listdir(d3)):
        print(f"  {f}")

# 看有没有终审结论
print("\n=== 章纲轮结果相关文件 ===")
for f in os.listdir(os.path.join(R, "_融合产物")):
    if "章纲" in f:
        p = os.path.join(R, "_融合产物", f)
        print(f"  {f}  ({'<DIR>' if os.path.isdir(p) else str(os.path.getsize(p))+' B'})")
