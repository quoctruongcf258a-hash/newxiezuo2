import json
from pathlib import Path
from urllib.request import urlopen

sys_path = r"F:\赛马23环整合工作室\程序2改装版\windows-use"

print("=" * 70)
print(" 扫描 9200-9260 端口")
print("=" * 70)
found = []
for port in range(9200, 9261):
    try:
        with urlopen(f"http://127.0.0.1:{port}/json", timeout=1) as f:
            pages = [t for t in json.load(f) if t.get("type") == "page"]
        if pages:
            title = pages[0].get("title", "")[:60]
            print(f"  ✅ :{port}  [{title}]")
            found.append((port, title))
    except Exception:
        pass

print(f"\n共找到 {len(found)} 个活跃端口")

print()
print("=" * 70)
print(" 查 apps.json 里所有 AI 配置")
print("=" * 70)
for ap in [Path(r"F:\赛马23环整合工作室\程序2改装版\rules\apps.json"),
           Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\apps.json")]:
    if ap.exists():
        data = json.loads(ap.read_text(encoding="utf-8"))
        apps = data.get("apps") or data.get("participants") or []
        print(f"\n📄 {ap.name}  ({len(apps)} 个 app)")
        for a in apps:
            if isinstance(a, dict):
                print(f"  key={a.get('key'):14} label={a.get('label', ''):14} cdpPort={a.get('cdpPort')}  exe={a.get('exe', '')[:50]}")

print()
print("=" * 70)
print(" mix_send 里注册的 AI")
print("=" * 70)
import sys
sys.path.insert(0, sys_path)
try:
    import mix_send
    cdp = mix_send.CDP_APPS
    print(f"  CDP_APPS 类型：{type(cdp)}")
    # 遍历
    if hasattr(cdp, 'keys'):
        for k in cdp.keys():
            print(f"    {k}: {cdp.get(k)}")
    elif hasattr(cdp, '_data'):
        for k, v in cdp._data.items():
            print(f"    {k}: {v}")
    else:
        # 直接试 __iter__
        try:
            for k in cdp:
                print(f"    {k}: {cdp[k]}")
        except Exception:
            print(f"    无法遍历：{dir(cdp)[:20]}")
except Exception as e:
    print(f"  ❌ {e}")
