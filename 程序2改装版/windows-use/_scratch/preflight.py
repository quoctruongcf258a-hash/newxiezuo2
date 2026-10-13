import os, json, psutil
import pygetwindow as gw, win32process

WS = r"C:\mai\multi-ai-pipeline\windows-use"
ROOT = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(ROOT, "资料", "指令", "章纲轮")

P = [("CodeBuddy","CodeBuddy CN"),("QUEST","QoderCN"),("Doubao","TRAE SOLO CN"),
     ("Qianwen","qianwen"),("WorkBuddy","WorkBuddy"),("ZCode","ZCode")]

print("=== 1. 章纲轮指令文件 ===")
ok1 = True
for key, _ in P:
    fp = os.path.join(CMD, key + ".txt")
    if os.path.exists(fp):
        print(f"  ✅ {key}.txt  ({os.path.getsize(fp)//1024} KB)")
    else:
        print(f"  ❌ {key}.txt 不存在"); ok1 = False

print("\n=== 2. ai_coords.json ===")
c = json.load(open(os.path.join(WS, "ai_coords.json"), encoding="utf-8"))
ok2 = True
for key, _ in P:
    if key in c and "input_rel" in c[key]:
        print(f"  ✅ {key}  rel={c[key]['input_rel']}")
    else:
        print(f"  ❌ {key} 缺 input_rel"); ok2 = False

print("\n=== 3. 窗口状态 ===")
ok3 = True
for key, proc in P:
    pids = set()
    for x in psutil.process_iter(['name','pid']):
        n = x.info['name'] or ""
        if n.lower().startswith(proc.lower()): pids.add(x.info['pid'])
    found = False
    for w in gw.getAllWindows():
        if not w.title or w.width < 100 or w.height < 100: continue
        try:
            _, wp = win32process.GetWindowThreadProcessId(w._hWnd)
            if wp in pids:
                print(f"  ✅ {key:11} [{w.title}]  ({w.left},{w.top} {w.width}x{w.height})")
                found = True; break
        except: pass
    if not found:
        print(f"  ❌ {key}  ({proc}) 窗口没找到"); ok3 = False

print("\n" + ("="*50))
if ok1 and ok2 and ok3:
    print("✅ 全部就绪，可以跑 auto_outline.py")
else:
    print("❌ 有缺项，先补")
