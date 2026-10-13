import json, pygetwindow as gw, psutil, win32process

# 读坐标
fp = r"C:\mai\multi-ai-pipeline\windows-use\ai_coords.json"
c = json.load(open(fp, encoding="utf-8"))
print("=== 录的坐标 ===")
print(f"  Doubao: {c.get('Doubao')}")

# 找豆包窗口
pids = set()
for x in psutil.process_iter(['name','pid']):
    if (x.info['name'] or '').lower().startswith('doubao'):
        pids.add(x.info['pid'])
wins = []
for w in gw.getAllWindows():
    if not w.title or w.width < 200 or w.left < -10000: continue
    try:
        _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
        if wp in pids: wins.append(w)
    except: pass
wins.sort(key=lambda w: w.width*w.height, reverse=True)
print("\n=== 当前豆包窗口 ===")
for w in wins:
    print(f"  [{w.title[:50]}]  ({w.left},{w.top})  {w.width}x{w.height}")

if wins and "Doubao" in c:
    w = wins[0]
    rel = c["Doubao"]["input_rel"]
    px = int(w.left + rel[0] * w.width)
    py = int(w.top + rel[1] * w.height)
    print(f"\n=== 按相对坐标算的点 ===")
    print(f"  点击位置: ({px}, {py})")
    print(f"  窗口范围: X={w.left}~{w.left+w.width}  Y={w.top}~{w.top+w.height}")
    if w.left <= px <= w.left+w.width and w.top <= py <= w.top+w.height:
        print("  ✅ 在窗口内")
    else:
        print("  ❌ 在窗口外")
