import os, time, json
import psutil, pyautogui, pyperclip
import pygetwindow as gw, win32process

WS = r"C:\mai\multi-ai-pipeline\windows-use"
CMD = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马\资料\指令\章纲轮"

P = [("CodeBuddy","CodeBuddy CN"),("QUEST","QoderCN"),("Doubao","Doubao"),
     ("Qianwen","qianwen"),("WorkBuddy","WorkBuddy"),("ZCode","ZCode")]

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

def send(key, proc, fp):
    cmd = open(fp, encoding="utf-8").read()
    w = find_win(proc)
    if not w: print(f"  找不到 {proc}"); return False
    print(f"  {w.title}")
    try:
        if w.isMinimized: w.restore()
        w.activate()
    except: pass
    time.sleep(1.2)
    c = json.load(open(os.path.join(WS, "ai_coords.json")))
    rel = c[key]["input_rel"]
    px = int(w.left + rel[0] * w.width)
    py = int(w.top  + rel[1] * w.height)
    pyautogui.click(px, py); time.sleep(0.4)
    pyautogui.click(px, py); time.sleep(0.8)
    pyperclip.copy(cmd); time.sleep(0.8)
    pyautogui.keyDown("ctrl"); time.sleep(0.1)
    pyautogui.press("v"); time.sleep(0.1)
    pyautogui.keyUp("ctrl"); time.sleep(2.5)
    pyautogui.press("enter"); time.sleep(0.5)
    return True

print("3 秒后开始，别碰键鼠...")
for i in range(3,0,-1): print(f"  {i}..."); time.sleep(1)

for key, proc in P:
    fp = os.path.join(CMD, key + ".txt")
    if not os.path.exists(fp): print(f"\n>>> {key} 无文件"); continue
    print(f"\n>>> {key} ({os.path.getsize(fp)//1024} KB)")
    if send(key, proc, fp): print("  OK")
    time.sleep(2)

print("\n全部完成")
