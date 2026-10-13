import psutil, pygetwindow as gw, win32process
import json, os

WS = r"C:\mai\multi-ai-pipeline\windows-use"
P = [("CodeBuddy","CodeBuddy CN"),("QUEST","QoderCN"),("Doubao","TRAE SOLO CN"),
     ("Qianwen","qianwen"),("WorkBuddy","WorkBuddy"),("ZCode","ZCode")]

c = json.load(open(os.path.join(WS, "ai_coords.json"), encoding="utf-8"))

print(f"{'key':11} {'窗口':35} {'新位置':>20} {'旧rect':>20} {'rel':>12}")
print("=" * 110)

for key, proc in P:
    pids = set()
    for x in psutil.process_iter(['name','pid']):
        n = x.info['name'] or ""
        if n.lower().startswith(proc.lower()): pids.add(x.info['pid'])
    for w in gw.getAllWindows():
        if not w.title or w.width < 100 or w.height < 100: continue
        try:
            _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
            if wp in pids:
                new = f"{w.left},{w.top} {w.width}x{w.height}"
                old = c.get(key, {}).get("window_rect", "?")
                rel = c.get(key, {}).get("input_rel", "?")
                oldstr = f"{old[0]},{old[1]} {old[2]}x{old[3]}" if isinstance(old, list) else str(old)
                print(f"{key:11} {w.title[:33]:35} {new:>20} {oldstr:>20} {str(rel):>12}")
                break
        except: pass
