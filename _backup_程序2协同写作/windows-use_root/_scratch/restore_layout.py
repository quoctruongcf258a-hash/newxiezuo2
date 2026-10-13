"""恢复保存的窗口布局"""
import pygetwindow as gw, json, psutil, win32process, time

LAYOUT = r"C:\mai\multi-ai-pipeline\windows-use\layout.json"

with open(LAYOUT, "r", encoding="utf-8") as f:
    layout = json.load(f)

# 每个 AI 的 (进程名, 标题关键词)
APPS = [
    ("CodeBuddy",  "CodeBuddy CN", ["CodeBuddy"]),
    ("QUEST",      "QoderCN",      ["Quest"]),
    ("TraeWork",   "TRAE SOLO CN", ["TraeWork"]),
    ("Qianwen",    "qianwen",      ["千问"]),
    ("WorkBuddy",  "WorkBuddy",    ["WorkBuddy"]),
    ("ZCode",      "ZCode",        ["ZCode"]),
    ("Doubao",     "Doubao",       ["豆包"]),
    ("DeepSeek",   "msedge",       ["DeepSeek"]),
]

def find_win(proc, title_kws):
    pids = set()
    for x in psutil.process_iter(['name','pid']):
        if (x.info['name'] or "").lower().startswith(proc.lower()):
            pids.add(x.info['pid'])
    wins = []
    for w in gw.getAllWindows():
        if not w.title or w.width < 100: continue
        try:
            _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
            if wp in pids:
                wins.append(w); continue
        except: pass
        for kw in title_kws:
            if kw.lower() in w.title.lower():
                wins.append(w); break
    if not wins: return None
    wins.sort(key=lambda w: w.width * w.height, reverse=True)
    return wins[0]

print("=== 恢复布局 ===")
for name, proc, kws in APPS:
    if name not in layout:
        print(f"  ⚠ {name} 不在布局中"); continue
    w = find_win(proc, kws)
    if not w:
        print(f"  ❌ {name} 找不到窗口"); continue
    p = layout[name]
    try:
        if w.isMinimized: w.restore()
        time.sleep(0.3)
        w.moveTo(p["x"], p["y"])
        time.sleep(0.2)
        w.resizeTo(p["width"], p["height"])
        time.sleep(0.3)
        print(f"  ✅ {name:12} → ({p['x']},{p['y']}) {p['width']}x{p['height']}")
    except Exception as e:
        print(f"  ⚠ {name}: {e}")

# UI 窗口
if "__UI__" in layout:
    for w in gw.getAllWindows():
        if not w.title: continue
        if "赛马全自动" in w.title:
            p = layout["__UI__"]
            try:
                if w.isMinimized: w.restore()
                time.sleep(0.3)
                w.moveTo(p["x"], p["y"])
                time.sleep(0.2)
                w.resizeTo(p["width"], p["height"])
                print(f"  ✅ UI → ({p['x']},{p['y']}) {p['width']}x{p['height']}")
            except Exception as e:
                print(f"  ⚠ UI: {e}")
            break

print("\n完成")
