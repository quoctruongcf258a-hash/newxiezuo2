import pygetwindow as gw, psutil, win32process

pids = set()
for x in psutil.process_iter(['name','pid']):
    if (x.info['name'] or "").lower().startswith("doubao"):
        pids.add(x.info['pid'])

print("=== 所有豆包窗口（可见）===")
i = 0
for w in gw.getAllWindows():
    if not w.title: continue
    if w.width < 100 or w.height < 100: continue
    if w.left < -10000: continue
    try:
        _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
        if wp in pids:
            print(f"  [{i}] 标题=[{w.title}]")
            print(f"       位置 ({w.left},{w.top})  大小 {w.width}x{w.height}")
            i += 1
    except: pass
print(f"\n共 {i} 个")
