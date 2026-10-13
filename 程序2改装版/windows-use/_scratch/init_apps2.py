import json, os, psutil

CFG = r"C:\mai\multi-ai-pipeline\config\ai_apps.json"
os.makedirs(os.path.dirname(CFG), exist_ok=True)

def find_exe(proc_name):
    for p in psutil.process_iter(['name','exe']):
        n = p.info['name'] or ""
        if n.lower().startswith(proc_name.lower()):
            return p.info['exe'] or ""
    return ""

PLAYERS = [
    {"名字": "CodeBuddy", "类型": "electron", "exe": find_exe("CodeBuddy"), "cdp_port": 9223, "进程名": "CodeBuddy CN", "启用": True},
    {"名字": "QUEST",     "类型": "electron", "exe": find_exe("QoderCN"),  "cdp_port": 9224, "进程名": "QoderCN", "启用": True},
    {"名字": "TraeWork",  "类型": "electron", "exe": find_exe("TRAE"),     "cdp_port": 9225, "进程名": "TRAE SOLO CN", "启用": True},
    {"名字": "Qianwen",   "类型": "electron", "exe": find_exe("qianwen"),  "cdp_port": 9226, "进程名": "qianwen", "启用": True},
    {"名字": "WorkBuddy", "类型": "electron", "exe": find_exe("WorkBuddy"),"cdp_port": 9227, "进程名": "WorkBuddy", "启用": True},
    {"名字": "ZCode",     "类型": "electron", "exe": find_exe("ZCode"),    "cdp_port": 9228, "进程名": "ZCode", "启用": True},
    {"名字": "Doubao",    "类型": "electron", "exe": r"F:\Program Files\com.tencent.pcgame.doubao\Doubao\app\Doubao.exe", "cdp_port": None, "进程名": "Doubao", "启用": True},
    {"名字": "DeepSeek",  "类型": "web", "浏览器": "msedge", "url": "https://chat.deepseek.com", "cdp_port": 9222, "启用": False},
]

json.dump(PLAYERS, open(CFG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"✅ 已写: {CFG}")
for p in PLAYERS:
    src = p.get("exe") or p.get("url") or "?"
    cdp = p.get("cdp_port") or "-"
    print(f"  [{'x' if p['启用'] else ' '}] {p['名字']:12}  CDP={str(cdp):6}  {src}")
