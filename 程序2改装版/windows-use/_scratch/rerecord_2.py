import pyautogui, json, os, time
import pygetwindow as gw

WS = r"C:\mai\multi-ai-pipeline\windows-use"
FP = os.path.join(WS, "ai_coords.json")

TARGETS = [
    ("CodeBuddy", "CodeBuddy CN", "CodeBuddy"),
    ("QUEST",     "QoderCN",      "Quest Window"),
]

for key, proc, hint in TARGETS:
    print("=" * 60)
    print(f"重录 [{key}]")
    print(f"1. 把窗口摆好、可见（标题：{hint}）")
    print(f"2. 鼠标移到它的【输入框中间】")
    print(f"3. 按 Enter")
    input("   准备好了按 Enter...")

    p = pyautogui.position()
    c = json.load(open(FP, encoding="utf-8"))
    c[key]["input_pos"] = [p.x, p.y]

    # 算相对坐标
    import psutil, win32process
    pids = set()
    for x in psutil.process_iter(['name','pid']):
        n = x.info['name'] or ""
        if n.lower().startswith(proc.lower()): pids.add(x.info['pid'])
    for w in gw.getAllWindows():
        if not w.title or w.width < 100: continue
        try:
            _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
            if wp in pids:
                rx = (p.x - w.left) / w.width
                ry = (p.y - w.top) / w.height
                c[key]["input_rel"] = [round(rx,4), round(ry,4)]
                c[key]["window_rect"] = [w.left, w.top, w.width, w.height]
                json.dump(c, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                print(f"   ✅ {key}  坐标 {p.x},{p.y}  窗口 [{w.title}] ({w.left},{w.top} {w.width}x{w.height})  相对 ({rx:.3f},{ry:.3f})\n")
                break
        except: pass

print("完成")
