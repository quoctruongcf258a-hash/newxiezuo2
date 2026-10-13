import json
from urllib.request import urlopen

port = 9223
print("=" * 70)
print(f"CodeBuddy 端口 {port} 的所有 CDP targets")
print("=" * 70)

try:
    with urlopen(f"http://127.0.0.1:{port}/json", timeout=3) as f:
        targets = json.load(f)
except Exception as e:
    print(f"❌ 连不上：{e}")
    raise SystemExit()

for i, t in enumerate(targets):
    print(f"\n[{i}] type={t.get('type')}")
    print(f"    title: {t.get('title', '')[:80]}")
    print(f"    url: {t.get('url', '')[:100]}")
    print(f"    id: {t.get('id', '')}")
    print(f"    ws: {t.get('webSocketDebuggerUrl', '')}")
