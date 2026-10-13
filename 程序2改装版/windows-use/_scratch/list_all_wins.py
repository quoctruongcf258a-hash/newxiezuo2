import pygetwindow as gw

print("=== 所有可见窗口 ===")
for w in gw.getAllWindows():
    if not w.title: continue
    if w.width < 30 or w.height < 30: continue
    if w.left < -10000: continue
    print(f"  [{w.title[:60]}]  ({w.left},{w.top})  {w.width}x{w.height}")
