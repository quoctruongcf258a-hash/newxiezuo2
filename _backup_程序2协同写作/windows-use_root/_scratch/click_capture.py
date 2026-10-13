"""点击定位器：你点击输入框，脚本记录坐标 + 当前窗口"""
import time, json, sys
import pyautogui
import psutil, pygetwindow as gw, win32process

# 用 pynput 监听鼠标点击
try:
    from pynput import mouse
except ImportError:
    print("需要 pynput: pip install pynput")
    sys.exit(1)

AI = sys.argv[1] if len(sys.argv) > 1 else "Qianwen"
PROC_MAP = {"CodeBuddy": "CodeBuddy CN", "Qianwen": "qianwen", "Doubao": "Doubao"}
proc = PROC_MAP[AI]

# 找窗口
pids = set()
for x in psutil.process_iter(['name','pid']):
    if (x.info['name'] or '').lower().startswith(proc.lower()):
        pids.add(x.info['pid'])
wins = []
for w in gw.getAllWindows():
    if not w.title or w.width < 200 or w.left < -10000: continue
    try:
        _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
        if wp in pids: wins.append(w)
    except: pass
if not wins:
    print(f"找不到 {AI} 窗口"); sys.exit(1)
wins.sort(key=lambda w: w.width*w.height, reverse=True)
win = wins[0]
print(f"{AI} 窗口: [{win.title}]")
print(f"位置: ({win.left},{win.top})  大小: {win.width}x{win.height}")
print()
print(f">>> 现在点击 {AI} 的输入框正中 <<<")
print("点击后脚本会自动记录坐标")
print()

captured = {}

def on_click(x, y, button, pressed):
    if not pressed:  # 只在按下时记录
        return
    captured["x"] = x
    captured["y"] = y
    return False  # 停止监听

with mouse.Listener(on_click=on_click) as listener:
    listener.join()

mx = captured["x"]
my = captured["y"]
print(f"\n捕获到点击: ({mx}, {my})")

# 检查是否在窗口内
if not (win.left <= mx <= win.left + win.width and win.top <= my <= win.top + win.height):
    print(f"⚠ 点击位置不在 {AI} 窗口内")
    print(f"   窗口范围: X={win.left}~{win.left+win.width}  Y={win.top}~{win.top+win.height}")
    sys.exit(1)

rx = (mx - win.left) / win.width
ry = (my - win.top) / win.height
print(f"相对坐标: ({rx:.4f}, {ry:.4f})")

# 保存
fp = r"C:\mai\multi-ai-pipeline\windows-use\ai_coords.json"
c = json.load(open(fp, encoding="utf-8"))
c[AI] = {
    "input_pos": [mx, my],
    "window_rect": [win.left, win.top, win.width, win.height],
    "input_rel": [round(rx, 4), round(ry, 4)],
}
json.dump(c, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"✅ {AI} 已保存")
