# list_quest_pages.py — 列出 QUEST 端口下所有 page
import json, urllib.request

with urllib.request.urlopen("http://127.0.0.1:9224/json", timeout=5) as f:
    pages = json.load(f)

print(f"共 {len(pages)} 个目标\n")
for i, p in enumerate(pages):
    if p.get("type") != "page":
        continue
    print(f"[{i}] type={p.get('type')}")
    print(f"    title: {p.get('title','')[:80]}")
    print(f"    url:   {p.get('url','')[:120]}")
    print()