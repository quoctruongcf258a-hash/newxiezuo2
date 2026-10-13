# show_ai_apps.py — 列出 ai_apps.json 里 4 个 AI 的配置
import json, sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import CFG_FILE, _load_cfg

print("配置文件:", CFG_FILE)
print()
for e in _load_cfg():
    n = e.get("名字")
    if n in ("WorkBuddy", "QUEST", "Doubao", "gemini"):
        print(f"  {n}:")
        print(f"    类型 = {e.get('类型')!r}")
        print(f"    cdp_port = {e.get('cdp_port')}")
        print(f"    url = {(e.get('url') or '')[:80]!r}")