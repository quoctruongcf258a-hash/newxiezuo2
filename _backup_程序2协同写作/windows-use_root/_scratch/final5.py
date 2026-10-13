import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
total = 0
for p in P:
    d = os.path.join(R, p, "评审", "章纲轮")
    files = sorted([f for f in os.listdir(d) if f.endswith(".md")]) if os.path.isdir(d) else []
    print(f"{p:12} {len(files)} 份")
    for f in files:
        print(f"    {f}  ({os.path.getsize(os.path.join(d,f))} B)")
    total += len(files)
print(f"\n合计 {total}/30")
