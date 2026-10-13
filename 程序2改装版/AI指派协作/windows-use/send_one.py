import os, sys, time, json
import psutil, pyautogui, pyperclip
import pygetwindow as gw, win32process

WS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "windows-use")

if len(sys.argv) < 3:
    print("用法: python send_one.py <key> <指令文件>")
    sys.exit(1)

key = sys.argv[1]
cmd_file = sys.argv[2]

PROC_MAP = {
    "CodeBuddy": "CodeBuddy CN",
    "QUEST":     "QoderCN",
    "Doubao":    "TRAE SOLO CN",
    "Qianwen":   "qianwen",
    "WorkBuddy": "WorkBuddy",
    "ZCode":     "ZCode",
}
proc = PROC_MAP.get(key)
if not proc:
    print(f"未知识别: {key}"); sys.exit(1)

def find_win(proc):
    pids = set()
    for x in psutil.process_iter(['name','pid']):
        n = x.info['name'] or ""
        if n.lower().startswith(proc.lower()): pids.add(x.info['pid'])
    best, area = None, 0
    for w in gw.getAllWindows():
        if not w.title or w.width < 100 or w.height < 100: continue
        try:
            _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
            if wp in pids:
                a = w.width * w.height
                if a > area: best, area = w, a
        except: pass
    return best

w = find_win(proc)
if not w:
    print(f"找不到 {proc}"); sys.exit(1)
print(f"窗口: [{w.title}]  ({w.left},{w.top} {w.width}x{w.height})")
try:
    if w.isMinimized: w.restore()
    w.activate()
except: pass
time.sleep(1.2)

c = json.load(open(os.path.join(WS, "ai_coords.json"), encoding="utf-8"))
rel = c[key]["input_rel"]
px = int(w.left + rel[0] * w.width)
py = int(w.top  + rel[1] * w.height)

text = open(cmd_file, encoding="utf-8").read()
print(f"指令大小: {len(text)//1024} KB")

pyautogui.click(px, py); time.sleep(0.4)
pyautogui.click(px, py); time.sleep(0.8)
pyperclip.copy(text); time.sleep(0.8)
pyautogui.keyDown("ctrl"); time.sleep(0.1)
pyautogui.press("v"); time.sleep(0.1)
pyautogui.keyUp("ctrl"); time.sleep(2.5)
pyautogui.press("enter")
print("✅ 已发送")
