import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
for p in P:
    d = os.path.join(R, p, "评审", "章纲轮")
    files = sorted([f for f in os.listdir(d) if f.endswith(".md")]) if os.path.isdir(d) else []
    print(f"{p}: {len(files)} 份  -> {files}")
