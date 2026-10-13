import sys, time
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from mix_send import send
for ai in ["CodeBuddy", "Doubao", "Qianwen"]:
    print(send(ai, f"【新坐标】{ai} 回OK"))
    time.sleep(2)
