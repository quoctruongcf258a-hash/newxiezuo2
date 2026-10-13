import pyautogui, time, json
import psutil, pygetwindow as gw, win32process

print("摆好 CodeBuddy 聊天窗口，鼠标停在【聊天输入框正中】，3 秒后记录")
for i in range(3, 0, -1):
    print(f"  {i}..."); time.sleep(1)

p = pyautogui.position()
print(f"鼠标位置: X={p.x}, Y={p.y}")

pids = set()
for x in psutil.process_iter(['name','pid']):
    if (x.info['name'] or "").lower().startswith("codebuddy"):
        pids.add(x.info['pid'])

# 找 CodeBuddy 主窗口（不含 Agents）
wins = []
for w in gw.getAllWindows():
    if not w.title or w.width < 100: continue
    try:
        _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
        if wp in pids and "CodeBuddy" in w.title and "Agents" not in w.title:
            wins.append(w)
    except: pass

if not wins:
    print("找不到 CodeBuddy 窗口"); exit()
# 选最大的
wins.sort(key=lambda w: w.width*w.height, reverse=True)
win = wins[0]
print(f"窗口: [{win.title}]  ({win.left},{win.top} {win.width}x{win.height})")
rx = (p.x - win.left) / win.width
ry = (p.y - win.top) / win.height
print(f"相对坐标: ({rx:.4f}, {ry:.4f})")

fp = r"C:\mai\multi-ai-pipeline\windows-use\ai_coords.json"
c = json.load(open(fp, encoding="utf-8"))
c["CodeBuddy"] = {
    "input_pos": [p.x, p.y],
    "window_rect": [win.left, win.top, win.width, win.height],
    "input_rel": [round(rx, 4), round(ry, 4)],
}
json.dump(c, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("✅ 已保存")
