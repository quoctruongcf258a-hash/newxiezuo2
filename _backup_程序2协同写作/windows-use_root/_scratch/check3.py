import json, pygetwindow as gw, psutil, win32process

fp = r"C:\mai\multi-ai-pipeline\windows-use\ai_coords.json"
c = json.load(open(fp, encoding="utf-8"))

PROC_MAP = {"CodeBuddy":"CodeBuddy CN","Qianwen":"qianwen","Doubao":"Doubao"}

for ai, proc in PROC_MAP.items():
    print(f"\n=== {ai} ===")
    if ai in c:
        print(f"  配置: input_pos={c[ai].get('input_pos')}")
        print(f"        window_rect={c[ai].get('window_rect')}")
        print(f"        input_rel={c[ai].get('input_rel')}")
    else:
        print("  配置: 无")
    # 当前窗口
    pids = set()
    for x in psutil.process_iter(['name','pid']):
        if (x.info['name'] or '').lower().startswith(proc.lower()):
            pids.add(x.info['pid'])
    for w in gw.getAllWindows():
        if not w.title or w.width < 200 or w.left < -10000: continue
        try:
            _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
            if wp in pids:
                print(f"  当前窗口: [{w.title[:30]}] ({w.left},{w.top} {w.width}x{w.height})")
                break
        except: pass
