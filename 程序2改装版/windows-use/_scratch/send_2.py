import sys, time, os
sys.path.insert(0, r"C:\mai\multi-ai-pipeline\windows-use")
from mix_send import send

CMD = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马\资料\指令\正文轮"
print("3 秒后开始，别碰键鼠...")
for i in range(3,0,-1): print(f"  {i}..."); time.sleep(1)

for ai in ["Qianwen", "Doubao"]:
    fp = os.path.join(CMD, ai + ".txt")
    if not os.path.exists(fp):
        print(f"{ai}: 文件不存在"); continue
    text = open(fp, encoding="utf-8").read()
    print(f"\n→ {ai}  ({len(text.encode('utf-8'))//1024} KB)")
    try:
        r = send(ai, text)
        print(f"  {r}")
    except Exception as e:
        print(f"  ❌ {e}")
    time.sleep(4)
print("\n完成")
