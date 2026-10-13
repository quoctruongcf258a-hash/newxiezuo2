import os, sys, time, json, argparse
import psutil, pyautogui, pyperclip
import pygetwindow as gw, win32process

WS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "windows-use")
CMD_DIR = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马\资料\指令\规划轮评审"
COORD_FILE = os.path.join(WS, "ai_coords.json")

PLAYERS = [
    ("CodeBuddy", "CodeBuddy CN", "CodeBuddy"),
    ("QUEST",     "QoderCN",      "QUEST"),
    ("Doubao",    "Doubao",       "豆包"),
    ("Qianwen",   "qianwen",      "千问"),
    ("WorkBuddy", "WorkBuddy",    "WorkBuddy"),
    ("ZCode",     "ZCode",        "ZCode"),
]

def find_win(proc):
    pids = set()
    for p in psutil.process_iter(['name','pid']):
        n = p.info['name'] or ""
        if n.lower().startswith(proc.lower()):
            pids.add(p.info['pid'])
    best, area = None, 0
    for w in gw.getAllWindows():
        if not w.title or w.width < 100 or w.height < 100: continue
        try:
            _, wpid = win32process.GetWindowThreadProcessId(w._hWnd)
            if wpid in pids:
                a = w.width * w.height
                if a > area: best, area = w, a
        except: pass
    return best

def send_one(key, proc, cf, wait_paste=2.0):
    with open(cf, "r", encoding="utf-8") as f:
        cmd = f.read()
    w = find_win(proc)
    if not w:
        print(f"  X 找不到 {proc} 窗口"); return False
    print(f"  窗口: [{w.title}] ({w.left},{w.top} {w.width}x{w.height})")
    try:
        if w.isMinimized: w.restore()
        w.activate()
    except Exception as e:
        print(f"  激活失败: {e}"); return False
    time.sleep(1.2)
    with open(COORD_FILE, "r", encoding="utf-8") as f:
        c = json.load(f)
    rel = c[key].get("input_rel")
    if not rel:
        print(f"  X {key} 没有 input_rel"); return False
    px = int(w.left + rel[0] * w.width)
    py = int(w.top  + rel[1] * w.height)
    print(f"  相对 {rel} -> 绝对 ({px}, {py})")
    pyautogui.click(px, py); time.sleep(0.4)
    pyautogui.click(px, py); time.sleep(0.8)
    pyperclip.copy(cmd)
    time.sleep(0.6)
    pyautogui.keyDown("ctrl"); time.sleep(0.1)
    pyautogui.press("v"); time.sleep(0.1)
    pyautogui.keyUp("ctrl")
    time.sleep(wait_paste)
    pyautogui.press("enter")
    time.sleep(0.5)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--wait", type=float, default=2.0)
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None
    print("=" * 60)
    print(f"发送 第 {args.batch} 批  (等待 {args.wait}s)")
    print("=" * 60)
    for i in range(3,0,-1): print(f"  {i}..."); time.sleep(1)
    sent, fail = [], []
    for key, proc, label in PLAYERS:
        if only and key not in only: continue
        cf = os.path.join(CMD_DIR, f"{key}_第{args.batch}批.txt")
        if not os.path.exists(cf):
            print(f"\n>>> {label} 无此批文件，跳过"); continue
        kb = os.path.getsize(cf)/1024
        print(f"\n>>> {label} ({proc}) {kb:.1f} KB")
        if send_one(key, proc, cf, wait_paste=args.wait):
            print("  OK 已发送"); sent.append(label)
        else:
            fail.append(label)
        time.sleep(2)
    print("\n" + "=" * 60)
    print(f"完成: {len(sent)} 成功 / {len(fail)} 失败")
    if fail: print("失败:", ", ".join(fail))
    print("=" * 60)

if __name__ == "__main__":
    main()