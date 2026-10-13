import sys
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from cdp_all import Tab

t = Tab(9222, "deepseek")
print("连上:", t.title)
t.write("用一句话回答：1+1等于几？")
t.send()
print("已发送，等回复...")
reply = t.wait_stable(seconds=3, max_wait=60)
print("\n=== DeepSeek 回复 ===")
print(reply[:500])
