import psutil, pygetwindow as gw, win32process

pids = set()
for x in psutil.process_iter(['name','pid']):
    if (x.info['name'] or "").lower() == "doubao":
        pids.add(x.info['pid'])

print("=== 豆包可见窗口 ===")
for w in gw.getAllWindows():
    if not w.title or w.width < 50: continue
    try:
        _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
        if wp in pids:
            print(f"  [{w.title}]  ({w.left},{w.top} {w.width}x{w.height})")
    except: pass
