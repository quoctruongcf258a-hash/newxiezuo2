import pyautogui, time, json
import psutil, pygetwindow as gw, win32process

print("=" * 60)
print("实时鼠标位置（每 0.5 秒刷新）")
print("把鼠标放到豆包输入框正中，位置对了按 Ctrl+C 停止")
print("=" * 60)

pids = set()
for x in psutil.process_iter(['name','pid']):
    if (x.info['name'] or "").lower() == "doubao":
        pids.add(x.info['pid'])

# 找豆包窗口
win = None
for w in gw.getAllWindows():
    if not w.title or w.width < 200: continue
    if not ("AI主管" in w.title or "豆包" in w.title or "Doubao" in w.title): continue
    try:
        _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
        if wp in pids:
            win = w; break
    except: pass

if win:
    print(f"豆包窗口: [{win.title}]  ({win.left},{win.top} {win.width}x{win.height})")
else:
    print("⚠ 没找到豆包窗口")

try:
    while True:
        p = pyautogui.position()
        line = f"鼠标: X={p.x:4} Y={p.y:4}"
        if win:
            rx = (p.x - win.left) / win.width
            ry = (p.y - win.top) / win.height
            line += f"   |  相对: ({rx:.4f}, {ry:.4f})"
        print(line, end="\r")
        time.sleep(0.3)
except KeyboardInterrupt:
    p = pyautogui.position()
    print(f"\n\n最终位置: X={p.x}, Y={p.y}")
    if win:
        rx = (p.x - win.left) / win.width
        ry = (p.y - win.top) / win.height
        print(f"相对坐标: ({rx:.4f}, {ry:.4f})")
        print(f"\n保存吗？(Enter 保存 / 输入 n 不保存)")
        ans = input().strip().lower()
        if ans != "n":
            fp = r"C:\mai\multi-ai-pipeline\windows-use\ai_coords.json"
            c = json.load(open(fp, encoding="utf-8"))
            c["Doubao"] = {
                "input_pos": [p.x, p.y],
                "window_rect": [win.left, win.top, win.width, win.height],
                "input_rel": [round(rx, 4), round(ry, 4)],
                "window_title": win.title,
            }
            json.dump(c, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            print("✅ 已保存")
