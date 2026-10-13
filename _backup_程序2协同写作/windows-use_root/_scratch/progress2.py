import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"

print("=== 章纲轮融合产物 ===")
d = os.path.join(R, "_融合产物", "章纲轮")
if os.path.isdir(d):
    for f in sorted(os.listdir(d)):
        fp = os.path.join(d, f)
        print(f"  {f}  ({os.path.getsize(fp)} B)  {os.path.getmtime(fp)}")
else:
    print("  目录不存在")

print("\n=== 章纲轮总稿 ===")
fp = os.path.join(R, "_融合产物", "融合_总稿_章纲轮.md")
print(f"  {'✅ 存在' if os.path.exists(fp) else '❌ 不存在'}"
      + (f"  ({os.path.getsize(fp)} B)" if os.path.exists(fp) else ""))

print("\n=== 章纲轮终审目录 ===")
for p in ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]:
    d2 = os.path.join(R, p, "评审", "章纲轮终审")
    if os.path.isdir(d2):
        files = [f for f in os.listdir(d2) if f.endswith(".md")]
        print(f"  {p:12} {len(files)} 份: {files}")

print("\n=== 章纲轮终审汇总目录 ===")
d3 = os.path.join(R, "_融合产物", "章纲轮终审汇总")
if os.path.isdir(d3):
    for f in sorted(os.listdir(d3)):
        print(f"  {f}")
else:
    print("  不存在")

print("\n=== 章纲轮所有相关产物 ===")
p = os.path.join(R, "_融合产物")
for f in sorted(os.listdir(p)):
    if "章纲" in f:
        fp = os.path.join(p, f)
        sz = "<DIR>" if os.path.isdir(fp) else f"{os.path.getsize(fp)} B"
        print(f"  {f}  ({sz})")
