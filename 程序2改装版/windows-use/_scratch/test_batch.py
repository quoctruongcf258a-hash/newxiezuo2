import sys, time
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from cdp_send import send

for name in ["QUEST","Doubao","WorkBuddy","ZCode","Qianwen","DeepSeek"]:
    r = send(name, f"【CDP测试】{name} 收到请回OK")
    print(r)
    time.sleep(1)
