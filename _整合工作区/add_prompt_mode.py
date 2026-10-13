# add_prompt_mode.py — 给 QUEST 加 prompt_mode: file（双保险）
import json
import shutil
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\ai_apps.json")
data = json.loads(P.read_text(encoding="utf-8"))

changed = 0
for e in data:
    if e.get("名字") == "QUEST" and e.get("prompt_mode") != "file":
        e["prompt_mode"] = "file"
        changed += 1
        print(f"✔ QUEST 加上 prompt_mode = file")

if changed:
    bak = P.with_suffix(".json.bak_promptmode")
    if not bak.exists():
        shutil.copy(P, bak)
        print(f"已备份：{bak.name}")
    P.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("已保存")
else:
    print("没有改动（已设置或找不到 QUEST）")