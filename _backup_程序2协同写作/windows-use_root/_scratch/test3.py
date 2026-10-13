import sys, time
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from mix_send import send
for ai in ["Qianwen", "CodeBuddy", "Doubao"]:
    print(send(ai, f"【新位置测】{ai} 回OK"))
    time.sleep(2)
