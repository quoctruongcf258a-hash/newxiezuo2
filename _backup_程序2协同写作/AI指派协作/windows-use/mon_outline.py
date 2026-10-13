import os, time
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
NEED = 5
start = time.time()
while True:
    os.system("cls" if os.name=="nt" else "clear")
    el = time.time() - start
    print(f"章纲轮监控  |  已过 {int(el//60)} 分 {int(el%60)} 秒  |  {time.strftime('%H:%M:%S')}")
    print("=" * 55)
    done = 0
    for p in P:
        d = os.path.join(R, p, "产出", "章纲轮")
        files = sorted([f for f in os.listdir(d) if f.endswith(".md")]) if os.path.isdir(d) else []
        n = len(files)
        bar = "█" * min(n, NEED) + "░" * max(0, NEED - n)
        mark = "✅" if n >= NEED else "⏳"
        print(f"  {mark} {p:12} {bar} {n}/{NEED}")
        if 0 < n < NEED:
            print(f"       最近: {files[-1]}")
        if n >= NEED: done += 1
    if done == 6:
        print("\n" + "=" * 55)
        print("🎉 章纲轮 6 家全部落盘")
        for p in P:
            d = os.path.join(R, p, "产出", "章纲轮")
            fs = sorted([f for f in os.listdir(d) if f.endswith(".md")]) if os.path.isdir(d) else []
            print(f"\n【{p}】{len(fs)} 份")
            for f in fs: print(f"   - {f}")
        break
    time.sleep(5)
