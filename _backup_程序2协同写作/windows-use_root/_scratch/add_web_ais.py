import json
CFG = r"C:\mai\multi-ai-pipeline\config\ai_apps.json"
apps = json.load(open(CFG, encoding="utf-8"))
web_ais = [
    {"名字": "Kimi",     "类型": "web", "url": "https://kimi.moonshot.cn",   "端口": 9222, "启用": False},
    {"名字": "Gemini",   "类型": "web", "url": "https://gemini.google.com",  "端口": 9222, "启用": False},
    {"名字": "通义",     "类型": "web", "url": "https://tongyi.aliyun.com",  "端口": 9222, "启用": False},
    {"名字": "元宝",     "类型": "web", "url": "https://yuanbao.tencent.com","端口": 9222, "启用": False},
]
existing = {p["名字"] for p in apps}
for w in web_ais:
    if w["名字"] not in existing:
        apps.append(w)
json.dump(apps, open(CFG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"现在 {len(apps)} 个 AI")
for p in apps:
    print(f"  [{'x' if p.get('启用') else ' '}] {p['名字']:12} {p.get('类型'):10} {p.get('exe') or p.get('url') or '-'}")
