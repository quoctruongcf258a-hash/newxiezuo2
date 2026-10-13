# fix_all_to_file.py — 一次性让 4 个 AI 全走文件模式
import json
import shutil
from pathlib import Path

TASKS = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
APPS = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\ai_apps.json")
changed = []

# ── 修 1：FILE_MODE_AIS 改成小写 + 判断加 .lower() ──
text = TASKS.read_text(encoding="utf-8")

OLD1 = 'FILE_MODE_AIS = {"QUEST", "WorkBuddy", "Doubao", "gemini"}'
if OLD1 in text:
    text = text.replace(OLD1, 'FILE_MODE_AIS = {"quest", "workbuddy", "doubao", "gemini"}', 1)
    changed.append("FILE_MODE_AIS 小写化")

OLD2 = 'if app.get("key") in FILE_MODE_AIS or app.get("prompt_mode") == "file":'
NEW2 = 'if (app.get("key") or "").lower() in FILE_MODE_AIS or app.get("prompt_mode") == "file":'
n = text.count(OLD2)
if n:
    text = text.replace(OLD2, NEW2)
    changed.append(f"{n} 处判断加 .lower()")

if changed:
    bak = TASKS.with_suffix(".py.bak_case")
    if not bak.exists():
        shutil.copy(TASKS, bak)
    TASKS.write_text(text, encoding="utf-8")
    for c in changed:
        print(f"✔ tasks.py: {c}")

# ── 修 2：ai_apps.json 里 4 个 AI 都加 prompt_mode=file（双保险）──
data = json.loads(APPS.read_text(encoding="utf-8"))
n2 = 0
for e in data:
    name = e.get("名字", "")
    if name in ("QUEST", "WorkBuddy", "Doubao", "gemini"):
        if e.get("prompt_mode") != "file":
            e["prompt_mode"] = "file"
            n2 += 1
            print(f"✔ ai_apps.json: {name} 加 prompt_mode=file")
if n2:
    bak2 = APPS.with_suffix(".json.bak_allfile")
    if not bak2.exists():
        shutil.copy(APPS, bak2)
    APPS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✔ ai_apps.json 已保存（改 {n2} 个）")
else:
    print("ai_apps.json 无需改动")