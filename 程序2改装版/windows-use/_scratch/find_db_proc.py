import pygetwindow as gw, psutil, win32process

print("=== 所有含'豆包'或'AI主管'的窗口，及所属进程 ===")
for w in gw.getAllWindows():
    if not w.title: continue
    if w.width < 100: continue
    if w.left < -10000: continue
    if not ("豆包" in w.title or "AI主管" in w.title or "Doubao" in w.title): continue
    try:
        _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
        try:
            pname = psutil.Process(wp).name()
        except:
            pname = "?"
        print(f"  窗口: [{w.title}]")
        print(f"    位置: ({w.left},{w.top})  {w.width}x{w.height}")
        print(f"    PID: {wp}  进程名: {pname}")
    except Exception as e:
        print(f"  窗口: [{w.title}]  错误: {e}")
