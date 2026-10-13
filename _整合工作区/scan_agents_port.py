import json
from urllib.request import urlopen

print("=" * 70)
print("① 扫描 9200-9250 端口，看 CodeBuddy Agents 用哪个")
print("=" * 70)
for port in range(9200, 9251):
    try:
        with urlopen(f"http://127.0.0.1:{port}/json", timeout=1) as f:
            targets = json.load(f)
        pages = [t for t in targets if t.get("type") == "page"]
        if pages:
            print(f"\n✅ :{port}  ({len(targets)} 个 target)")
            for t in targets:
                print(f"    type={t.get('type'):10}  title={t.get('title','')[:60]}")
    except Exception:
        pass

print()
print("=" * 70)
print("② 所有端口里，含「输入消息」或「Agents」的 target")
print("=" * 70)
for port in range(9200, 9251):
    try:
        with urlopen(f"http://127.0.0.1:{port}/json", timeout=1) as f:
            targets = json.load(f)
        for t in targets:
            title = t.get("title", "")
            url = t.get("url", "")
            if "Agents" in title or "Agents" in url or "输入消息" in title:
                print(f"  :{port}  type={t.get('type')}  title={title[:80]}")
                print(f"         url={url[:100]}")
    except Exception:
        pass
