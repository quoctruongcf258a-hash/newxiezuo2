import sys, time
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from cdp_send_all import send

for name in ["ZCode","QUEST","Doubao","WorkBuddy","Qianwen","DeepSeek"]:
    r = send(name, f"【ALL测】{name} 收到回OK")
    print(r)
    time.sleep(1.5)
