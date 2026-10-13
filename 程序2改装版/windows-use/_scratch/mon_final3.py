import os, time
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
start = time.time()
while True:
    os.system("cls")
    el = time.time() - start
    print(f"章纲轮终审监控  |  {int(el//60)}分{int(el%60)}秒")
    print("=" * 55)
    done = 0
    for p in P:
        fp = os.path.join(R, p, "评审", "章纲轮终审", f"{p}.md")
        if os.path.exists(fp):
            print(f"  OK {p:12} {os.path.getsize(fp)} B")
            done += 1
        else:
            print(f"  -- {p:12} 等待中")
    if done == 6:
        print("\n" + "=" * 55)
        print("6/6 全部完成！")
        break
    time.sleep(10)
