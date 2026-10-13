import sys, time
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from mix_send import send

for name in ["ZCode", "QUEST", "TraeWork", "WorkBuddy", "DeepSeek"]:
    r = send(name, f"【回车测】{name} 收到回OK")
    print(r)
    time.sleep(1.5)
