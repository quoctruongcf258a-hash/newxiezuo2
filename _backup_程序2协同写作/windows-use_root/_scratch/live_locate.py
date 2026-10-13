"""实时定位器：移动鼠标 → 屏幕显示坐标 → 按 Enter 记录"""
import pyautogui, json, os, time, threading, sys
import psutil, pygetwindow as gw, win32process

# 找窗口
def find_win():
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
    return wins[0] if wins else None

win = find_win()
if not win:
    print("找不到豆包窗口"); sys.exit()
print(f"豆包窗口: [{win.title}]")
print(f"位置: ({win.left},{win.top})  大小: {win.width}x{win.height}")
print()
print("操作：移动鼠标到豆包输入框正中，看着屏幕上的坐标")
print("坐标准确后，按 Enter 记录（或 Ctrl+C 取消）")
print()

stop = False
def monitor():
    while not stop:
        p = pyautogui.position()
        rx = (p.x - win.left) / win.width
        ry = (p.y - win.top) / win.height
        # 用 \r 覆盖一行
        sys.stdout.write(f"\r鼠标: X={p.x:4d}  Y={p.y:4d}   相对: ({rx:.4f}, {ry:.4f})")
        sys.stdout.flush()
        time.sleep(0.15)

threading.Thread(target=monitor, daemon=True).start()

try:
    input()
except KeyboardInterrupt:
    pass
stop = True

p = pyautogui.position()
rx = (p.x - win.left) / win.width
ry = (p.y - win.top) / win.height
print(f"\n\n最终位置: X={p.x} Y={p.y}  相对: ({rx:.4f}, {ry:.4f})")

if 0 <= rx <= 1 and 0 <= ry <= 1:
    fp = r"C:\mai\multi-ai-pipeline\windows-use\ai_coords.json"
    c = json.load(open(fp, encoding="utf-8"))
    c["Doubao"] = {
        "input_pos": [p.x, p.y],
        "window_rect": [win.left, win.top, win.width, win.height],
        "input_rel": [round(rx, 4), round(ry, 4)],
    }
    json.dump(c, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("✅ 已保存")
else:
    print("⚠ 鼠标不在窗口内")
