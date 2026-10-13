import sys, time
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from cdp_all import open_app

for name in ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]:
    try:
        t = open_app(name)
        print(f"\n=== {name} ===  {t.title[:50]}")
        r1 = t.write(f"【CDP探针】{name} 收到请回 OK")
        time.sleep(0.3)
        r2 = t.send()
        print(f"  写入: {r1}   发送: {r2}")
    except Exception as e:
        print(f"\n=== {name} === ❌ {e}")
