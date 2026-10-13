import sys, time
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from mix_send import send

CMD_FILE = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马\资料\指令\章纲轮终审\公共.txt"
text = open(CMD_FILE, encoding="utf-8").read()
print(f"指令大小: {len(text)//1024} KB")

print("3 秒后开始，别碰键鼠...")
for i in range(3,0,-1):
    print(f"  {i}..."); time.sleep(1)

AI_ORDER = ["ZCode", "QUEST", "TraeWork", "WorkBuddy", "DeepSeek", "Qianwen", "CodeBuddy", "Doubao"]
for i, ai in enumerate(AI_ORDER, 1):
    print(f"\n[{i}/{len(AI_ORDER)}] → {ai}")
    try:
        r = send(ai, text)
        print(f"  {r}")
    except Exception as e:
        print(f"  ❌ {e}")
    time.sleep(3)

print("\n全部发送完成")
