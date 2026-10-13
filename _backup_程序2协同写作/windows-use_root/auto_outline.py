import os, time, json
import psutil, pyautogui, pyperclip
import pygetwindow as gw, win32process

WS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "windows-use")
ROOT = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD_DIR = os.path.join(ROOT, "资料", "指令", "章纲轮")
OUT_DIR = "产出/章纲轮"
NEED = 5
TIMEOUT_MIN = 60

PLAYERS = [
    ("CodeBuddy", "CodeBuddy CN"),
    ("QUEST",     "QoderCN"),
    ("Doubao",    "TRAE SOLO CN"),   # 豆包位置现由 TraeWork 顶替
    ("Qianwen",   "qianwen"),
    ("WorkBuddy", "WorkBuddy"),
    ("ZCode",     "ZCode"),
]

def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

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

def send(key, proc, text):
    w = find_win(proc)
    if not w: log(f"  X 找不到 {proc}"); return False
    log(f"  窗口: {w.title}")
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

def count(p):
    d = os.path.join(ROOT, p, OUT_DIR)
    return len([f for f in os.listdir(d) if f.endswith(".md")]) if os.path.isdir(d) else 0

def main():
    log("=" * 60)
    log("章纲轮 · 出稿 · 全自动")
    log("=" * 60)
    log("3 秒后开始，别碰键鼠...")
    for i in range(3,0,-1):
        print(f"  {i}..."); time.sleep(1)

    log("【阶段1】发送指令到 6 个窗口")
    for key, proc in PLAYERS:
        fp = os.path.join(CMD_DIR, key + ".txt")
        if not os.path.exists(fp):
            log(f"  跳过 {key}（无指令文件）"); continue
        text = open(fp, encoding="utf-8").read()
        kb = len(text) // 1024
        log(f"  → {key} ({kb} KB)")
        if not send(key, proc, text):
            log(f"    重试...")
            time.sleep(3)
            send(key, proc, text)
        time.sleep(2)

    log("【阶段2】等待落盘")
    start = time.time()
    last_log = 0
    last_status = None
    while True:
        el = (time.time() - start) / 60
        if el > TIMEOUT_MIN:
            log(f"X 超时（{TIMEOUT_MIN} 分钟）")
            return
        done = 0
        status = []
        for p, _ in PLAYERS:
            n = count(p)
            status.append(f"{p}:{n}")
            if n >= NEED: done += 1
        cur = "|".join(status)
        if cur != last_status or time.time() - last_log > 30:
            log(f"  [{int(el)}分] " + "  ".join(f"{p} {count(p)}/{NEED}" for p, _ in PLAYERS))
            last_status = cur
            last_log = time.time()
        if done == 6:
            log("🎉 章纲轮出稿全部完成")
            return
        time.sleep(10)

if __name__ == "__main__":
    main()
