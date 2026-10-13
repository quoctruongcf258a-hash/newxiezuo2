import sys, json
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")

# 1. 读 today.json
print("=" * 70)
print("① _scratch/today.json 当前 opened")
print("=" * 70)
f = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\today.json")
data = json.loads(f.read_text(encoding="utf-8"))
for x in data.get("opened", []):
    print(f"  {x['key']:12}  cdpPort={x.get('cdpPort')}")

# 2. 检查 mix_send 能否识别
print()
print("=" * 70)
print("② mix_send 各 AI 忙闲")
print("=" * 70)
try:
    from mix_send import is_ai_busy
    for ai in ["workbuddy", "doubao", "codebuddy", "gemini"]:
        try:
            busy = is_ai_busy(ai)
            print(f"  {ai:12}: {'忙' if busy else '闲'}")
        except Exception as e:
            print(f"  {ai:12}: err({e})")
except Exception as e:
    print(f"  ❌ mix_send 导入失败：{e}")

# 3. CDP 端口
print()
print("=" * 70)
print("③ CDP 端口连通性")
print("=" * 70)
for ai, port in [("workbuddy", 9227), ("doubao", 9231), ("codebuddy", 9223), ("gemini", 9239)]:
    try:
        with urlopen(f"http://127.0.0.1:{port}/json", timeout=2) as r:
            pages = [t for t in json.load(r) if t.get("type") == "page"]
        ttl = pages[0].get("title", "")[:40] if pages else "无页面"
        print(f"  OK {ai:12} :{port}  [{ttl}]")
    except Exception as e:
        print(f"  NG {ai:12} :{port}  {type(e).__name__}")
