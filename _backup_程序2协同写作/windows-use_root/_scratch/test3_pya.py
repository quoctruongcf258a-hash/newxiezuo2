import sys, time
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from mix_send import send

for ai in ["Qianwen", "CodeBuddy", "Doubao"]:
    r = send(ai, f"【位置测】{ai} 回OK")
    print(r)
    time.sleep(2)
