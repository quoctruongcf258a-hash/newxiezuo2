# check_aimode.py — 查 ai_apps.json 里各 AI 的 prompt_mode
import json
from pathlib import Path

p = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\ai_apps.json")
data = json.loads(p.read_text(encoding="utf-8"))
for e in data:
    n = e.get("名字")
    if n in ("QUEST", "Doubao", "gemini", "WorkBuddy"):
        mode = e.get("prompt_mode", "(未设置)")
        t = e.get("类型", "")
        print(f"{n:12s}  类型={t}  prompt_mode={mode}")