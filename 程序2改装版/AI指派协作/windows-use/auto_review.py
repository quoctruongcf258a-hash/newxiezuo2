import os, time, json
import psutil, pyautogui, pyperclip
import pygetwindow as gw, win32process

WS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "windows-use")
ROOT = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(ROOT, "资料", "指令", "章纲轮评审")
NEED = 5

P = [
    ("CodeBuddy", "CodeBuddy CN"),
    ("QUEST",     "QoderCN"),
    ("Doubao",    "TRAE SOLO CN"),
    ("Qianwen",   "qianwen"),
    ("WorkBuddy", "WorkBuddy"),
    ("ZCode",     "ZCode"),
]

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

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
    text = open(fp, encoding="utf-8").read()
    w = find_win(proc)
    if not w: log(f"  X 找不到 {proc}"); return False
    try:
        if w.isMinimized: w.restore()
        w.activate()
    except: pass
    time.sleep(1.2)
    c = json.load(open(os.path.join(WS, "ai_coords.json"), encoding="utf-8"))
    rel = c[key]["input_rel"]
    px = int(w.left + rel[0] * w.width)
    py = int(w.top  + rel[1] * w.height)
    pyautogui.click(px, py); time.sleep(0.4)
    pyautogui.click(px, py); time.sleep(0.8)
    pyperclip.copy(text); time.sleep(0.8)
    pyautogui.keyDown("ctrl"); time.sleep(0.1)
    pyautogui.press("v"); time.sleep(0.1)
    pyautogui.keyUp("ctrl"); time.sleep(2.5)
    pyautogui.press("enter"); time.sleep(0.5)
    return True

def count_reviews(p):
    d = os.path.join(ROOT, p, "评审", "章纲轮")
    return len([f for f in os.listdir(d) if f.endswith(".md")]) if os.path.isdir(d) else 0

def run_batch(b):
    log(f"======== 第 {b} 批 发送 ========")
    for key, proc in P:
        fp = os.path.join(CMD, f"{key}_第{b}批.txt")
        if not os.path.exists(fp): log(f"  跳过 {key}"); continue
        log(f"  → {key} ({os.path.getsize(fp)//1024} KB)")
        if not send(key, proc, fp):
            time.sleep(3); send(key, proc, fp)
        time.sleep(2)
    log(f"======== 第 {b} 批 等待落盘 ========")
    start = time.time()
    last = 0
    while True:
        el = (time.time() - start) / 60
        if el > 45:
            log(f"  超时"); return False
        done = 0
        for p, _ in P:
            if count_reviews(p) >= b: done += 1
        if time.time() - last > 30:
            log(f"  [{int(el)}分] " + "  ".join(f"{p} {count_reviews(p)}/{b}" for p, _ in P))
            last = time.time()
        if done == 6:
            log(f"  第 {b} 批全部落盘")
            return True
        time.sleep(10)

def main():
    log("章纲轮互审 · 全自动")
    log("3 秒后开始，别碰键鼠...")
    for i in range(3,0,-1):
        print(f"  {i}..."); time.sleep(1)
    for b in [1,2,3,4,5]:
        if not run_batch(b):
            log(f"第 {b} 批未完成，停下")
            return
        time.sleep(5)
    log("🎉 章纲轮互审全部完成（30 份）")

if __name__ == "__main__":
    main()
