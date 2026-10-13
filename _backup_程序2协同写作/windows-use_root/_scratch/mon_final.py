import os, time
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
NEED = 1
start = time.time()
while True:
    os.system("cls")
    elapsed = time.time() - start
    done = 0
    print(f"监控中  |  已过 {int(elapsed//60)} 分 {int(elapsed%60)} 秒")
    print("=" * 50)
    for p in P:
        d = os.path.join(R, p, "评审", "规划轮终审")
        n = len([f for f in os.listdir(d) if f.endswith(".md")]) if os.path.isdir(d) else 0
        mark = "✅" if n >= NEED else "⏳"
        bar = "█" * n + "░" * max(0, NEED-n)
        print(f"  {mark} {p:12} {bar} {n}/{NEED}")
        if n >= NEED: done += 1
    if done == 6:
        print("\n🎉 6 家终审全部落盘")
        break
    time.sleep(5)
