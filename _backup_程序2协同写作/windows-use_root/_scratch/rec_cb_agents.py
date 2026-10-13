import pyautogui, time, json
import psutil, pygetwindow as gw, win32process

pids = set()
for x in psutil.process_iter(['name','pid']):
    if (x.info['name'] or "").lower().startswith("codebuddy"):
        pids.add(x.info['pid'])

# 只找 Agents 窗口
win = None
for w in gw.getAllWindows():
    if not w.title or w.width < 100: continue
    if "Agents" not in w.title: continue
    try:
        _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
        if wp in pids:
            win = w; break
    except: pass

if not win:
    print("❌ 找不到 Agents 窗口"); exit()
print(f"Agents 窗口: ({win.left},{win.top} {win.width}x{win.height})")

print("\n3 秒内把鼠标移到 Agents 窗口的【聊天输入框正中】")
for i in range(3, 0, -1):
    print(f"  {i}..."); time.sleep(1)

p = pyautogui.position()
print(f"鼠标: X={p.x}, Y={p.y}")
rx = (p.x - win.left) / win.width
ry = (p.y - win.top) / win.height
print(f"相对坐标: ({rx:.4f}, {ry:.4f})")

if 0 <= rx <= 1 and 0 <= ry <= 1:
    fp = r"C:\mai\multi-ai-pipeline\windows-use\ai_coords.json"
    c = json.load(open(fp, encoding="utf-8"))
    c["CodeBuddy"] = {
        "input_pos": [p.x, p.y],
        "window_rect": [win.left, win.top, win.width, win.height],
        "input_rel": [round(rx, 4), round(ry, 4)],
        "window_title": "Agents",
    }
    json.dump(c, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("✅ 已保存（窗口类型=Agents）")
else:
    print("⚠ 鼠标不在 Agents 窗口内")
