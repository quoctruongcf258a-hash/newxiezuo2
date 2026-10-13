import json, urllib.request

with urllib.request.urlopen("http://127.0.0.1:9223/json", timeout=5) as f:
    tabs = json.load(f)

print(f"共 {len(tabs)} 个 target:")
for t in tabs:
    print(f"\n  type={t.get('type')}")
    print(f"  title={t.get('title','')[:60]}")
    print(f"  url={t.get('url','')[:100]}")
    print(f"  ws={t.get('webSocketDebuggerUrl','')[:80]}")
