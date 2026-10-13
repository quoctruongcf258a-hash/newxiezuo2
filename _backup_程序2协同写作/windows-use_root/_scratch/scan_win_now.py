import psutil, pygetwindow as gw, win32process

targets = ["CodeBuddy","Doubao","qianwen","QoderCN","TRAE","WorkBuddy","ZCode","TraeWork","Trae"]
pids = {}
for p in psutil.process_iter(['name','pid']):
    n = p.info['name'] or ""
    for t in targets:
        if t.lower() in n.lower():
            pids[p.info['pid']] = n

print("=== 进程 ===")
for pid, n in sorted(pids.items(), key=lambda x:x[1]):
    print(f"  PID {pid}  {n}")

print("\n=== 窗口 ===")
for w in gw.getAllWindows():
    if not w.title or w.width < 100 or w.height < 100: continue
    try:
        _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
        if wp in pids:
            print(f"  [{w.title}]  ({w.left},{w.top} {w.width}x{w.height})  进程={pids[wp]}")
    except: pass
