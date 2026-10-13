import json, shutil
from pathlib import Path

root = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use")
targets = [
    root / "_scratch" / "today.json",
    root / "today.json",
]

codebuddy_item = {
    "key": "codebuddy",
    "label": "CodeBuddy",
    "vendor": "",
    "region": "国内",
    "form": "desktop",
    "target": "",           # CDP 模式不需要 exe 路径
    "browser": "msedge",
    "cdpPort": 9223,
    "cdpMatch": "codebuddy"
}

for f in targets:
    if not f.exists():
        print(f"[SKIP] 不存在：{f}")
        continue

    data = json.loads(f.read_text(encoding="utf-8"))
    opened = data.get("opened") or []

    new_opened = []
    changed = False
    for item in opened:
        if item.get("key") == "quest":
            print(f"  [{f.parent.name}/{f.name}] 替换 quest → codebuddy")
            new_opened.append(codebuddy_item)
            changed = True
        else:
            new_opened.append(item)

    if not changed:
        print(f"  [{f.parent.name}/{f.name}] 未找到 quest，跳过")
        continue

    data["opened"] = new_opened

    bak = f.with_suffix(".json.bak_swap_ai")
    if not bak.exists():
        shutil.copy(f, bak)
        print(f"    已备份：{bak.name}")

    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"    已写回")
    print(f"    新 opened keys: {[x['key'] for x in new_opened]}")

print("\n=== 完成 ===")
