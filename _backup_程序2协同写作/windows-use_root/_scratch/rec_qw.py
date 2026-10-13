import pyautogui, time, json
import psutil, pygetwindow as gw, win32process

print("摆好千问窗口，鼠标停在【输入框正中】，3 秒后记录")
for i in range(3, 0, -1):
    print(f"  {i}..."); time.sleep(1)

p = pyautogui.position()
print(f"鼠标位置: X={p.x}, Y={p.y}")

pids = set()
for x in psutil.process_iter(['name','pid']):
    if (x.info['name'] or "").lower().startswith("qianwen"):
        pids.add(x.info['pid'])
win = None
for w in gw.getAllWindows():
    if not w.title or w.width < 100: continue
    try:
        _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
        if wp in pids: win = w; break
    except: pass

if not win:
    print("找不到千问窗口"); exit()
print(f"千问窗口: [{win.title}]  ({win.left},{win.top} {win.width}x{win.height})")
rx = (p.x - win.left) / win.width
ry = (p.y - win.top) / win.height
print(f"相对坐标: ({rx:.4f}, {ry:.4f})")

fp = r"C:\mai\multi-ai-pipeline\windows-use\ai_coords.json"
c = json.load(open(fp, encoding="utf-8"))
c["Qianwen"] = {
    "input_pos": [p.x, p.y],
    "window_rect": [win.left, win.top, win.width, win.height],
    "input_rel": [round(rx, 4), round(ry, 4)],
}
json.dump(c, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("✅ 已保存")
