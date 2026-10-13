"""保存所有窗口位置（AI + UI），双策略：进程名 + 标题兜底"""
import pygetwindow as gw, json, psutil, win32process

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

layout = {}
for name, proc, title_kws in APPS:
    pids = set()
    for x in psutil.process_iter(['name','pid']):
        if (x.info['name'] or "").lower().startswith(proc.lower()):
            pids.add(x.info['pid'])
    wins = []
    for w in gw.getAllWindows():
        if not w.title or w.width < 100 or w.height < 100: continue
        if w.left < -10000: continue
        # 策略1：按进程名
        try:
            _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
            if wp in pids:
                wins.append(w); continue
        except: pass
        # 策略2：按标题
        for kw in title_kws:
            if kw.lower() in w.title.lower():
                wins.append(w); break
    if not wins:
        print(f"  ❌ {name}  找不到窗口")
        continue
    wins.sort(key=lambda w: w.width * w.height, reverse=True)
    w = wins[0]
    layout[name] = {"title": w.title, "x": w.left, "y": w.top, "width": w.width, "height": w.height}
    print(f"  ✅ {name:12} [{w.title[:35]}]  ({w.left},{w.top})  {w.width}x{w.height}")

# UI 窗口
for w in gw.getAllWindows():
    if not w.title: continue
    if w.width < 100 or w.left < -10000: continue
    if "赛马全自动" in w.title:
        layout["__UI__"] = {"title": w.title, "x": w.left, "y": w.top, "width": w.width, "height": w.height}
        print(f"  ✅ UI [{w.title}]  ({w.left},{w.top})  {w.width}x{w.height}")
        break

fp = r"C:\mai\multi-ai-pipeline\windows-use\layout.json"
json.dump(layout, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n✅ 布局已保存到 {fp}  （{len(layout)} 个窗口）")
