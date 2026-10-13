import sys
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from cdp_all import open_app

# 打开 CodeBuddy
t = open_app("CodeBuddy")
print("连上:", t.title)

# 写入 + 发送
t.write("【CDP演示】你好，请回一句话")
t.send()
print("已发送，等回复...")

# 读回复
reply = t.wait_stable(seconds=3, max_wait=90)
print("\n=== CodeBuddy 回复 ===")
print(reply[:600])
