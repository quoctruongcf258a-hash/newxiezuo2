import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"

# 1. 融合总稿
F = os.path.join(R, "_融合产物", "融合_总稿_规划轮.md")
t = open(F, encoding="utf-8").read()
print("融合总稿:", os.path.getsize(F), "字节")
print("前 200 字:")
print(t[:200])
print("\n含 '融合官' 吗:", "融合官" in t)
print("含 'QUEST' 吗:", "QUEST" in t)

# 2. CodeBuddy 的 A2 任务书
fp = os.path.join(R, "CodeBuddy", "A2_章纲任务书.md")
print("\n\n=== CodeBuddy/A2_章纲任务书.md ===")
print(open(fp, encoding="utf-8").read())
