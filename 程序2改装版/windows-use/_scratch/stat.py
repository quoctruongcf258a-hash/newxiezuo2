import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
for p in ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]:
    d = os.path.join(R, p, "评审", "规划轮")
    if not os.path.isdir(d):
        print(f"【{p}】目录不存在")
        continue
    files = sorted([f for f in os.listdir(d) if f.endswith(".md")])
    print(f"\n【{p}】{len(files)} 份")
    for f in files:
        print(f"   - {f}  ({os.path.getsize(os.path.join(d,f))} B)")