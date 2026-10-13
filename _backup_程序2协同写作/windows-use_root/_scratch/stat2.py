import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"

EXPECT = {
    "CodeBuddy": ["WorkBuddy","Qianwen","QUEST","ZCode","Doubao"],
    "QUEST":     ["WorkBuddy","CodeBuddy","Qianwen","ZCode","Doubao"],
    "Doubao":    ["WorkBuddy","CodeBuddy","Qianwen","QUEST","ZCode"],
    "Qianwen":   ["WorkBuddy","CodeBuddy","ZCode","Doubao","QUEST"],
    "WorkBuddy": ["Qianwen","QUEST","ZCode","Doubao","CodeBuddy"],
    "ZCode":     ["WorkBuddy","CodeBuddy","Qianwen","QUEST","Doubao"],
}

for p, expect in EXPECT.items():
    d = os.path.join(R, p, "评审", "规划轮")
    files = sorted([f for f in os.listdir(d) if f.endswith(".md")]) if os.path.isdir(d) else []
    have = set(f.replace("评审_","").replace(".md","") for f in files)
    miss = [x for x in expect if x not in have]
    extra = [x for x in have if x not in expect]
    status = "✅" if not miss else "⏳"
    print(f"{status} 【{p}】{len(files)} 份")
    if miss: print(f"    缺: {miss}")
    if extra: print(f"    多: {extra}")

print("\n共应有 6×5 = 30 份")
total = sum(len([f for f in os.listdir(os.path.join(R,p,"评审","规划轮")) if f.endswith(".md")]) for p in EXPECT if os.path.isdir(os.path.join(R,p,"评审","规划轮")))
print(f"实有 {total} 份")