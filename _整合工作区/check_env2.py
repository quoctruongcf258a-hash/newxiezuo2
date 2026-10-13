import sys, json
from pathlib import Path

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")

print("=" * 70)
print("① mix_send 的 AI 配置清单")
print("=" * 70)
try:
    import mix_send
    print(f"  CDP_APPS（走 CDP）：")
    for k, v in (mix_send.CDP_APPS or {}).items():
        print(f"    {k}: {v}")
    print(f"\n  PYA_APPS（走 pyautogui）：")
    for k, v in (mix_send.PYA_APPS or {}).items():
        print(f"    {k}: {v}")
except Exception as e:
    print(f"  ❌ {e}")

print()
print("=" * 70)
print("② 每个 AI 的忙闲状态（用 is_ai_busy 完整测）")
print("=" * 70)
for ai in ["workbuddy", "doubao", "quest", "gemini"]:
    try:
        from mix_send import is_ai_busy
        busy = is_ai_busy(ai)
        print(f"  {ai:12}: {'忙' if busy else '闲'}")
    except Exception as e:
        print(f"  {ai:12}: err({e})")

print()
print("=" * 70)
print("③ 检查 gemini 可能的端口")
print("=" * 70)
from urllib.request import urlopen
for port in range(9220, 9240):
    try:
        with urlopen(f"http://127.0.0.1:{port}/json", timeout=1) as f:
            pages = [t for t in json.load(f) if t.get("type") == "page"]
        if pages:
            print(f"  ✅ :{port}  [{pages[0].get('title', '')[:50]}]")
    except Exception:
        pass

print()
print("=" * 70)
print("④ apps.json 里的 AI 定义")
print("=" * 70)
apps_paths = [
    Path(r"F:\赛马23环整合工作室\程序2改装版\rules\apps.json"),
    Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\apps.json"),
]
for ap in apps_paths:
    if ap.exists():
        try:
            data = json.loads(ap.read_text(encoding="utf-8"))
            print(f"\n  📄 {ap.name}")
            # 找 participants / apps 之类
            for key in ["participants", "apps", "ais", "AIs"]:
                if key in data:
                    print(f"    {key}:")
                    for item in data[key]:
                        if isinstance(item, dict):
                            print(f"      {item.get('key')}: {item.get('label')}, cdpPort={item.get('cdpPort')}")
        except Exception as e:
            print(f"  ❌ 读 {ap}: {e}")
