# drop_ai_items.py — 删质检「十五 AI 使用合规质检」里的 3 项
import json
import shutil
from pathlib import Path

TARGETS = [
    Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\apps.json"),
]

DROP = {"AI 生成比例", "AI 版权风险", "是否违反平台 AI 政策"}

for t in TARGETS:
    if not t.exists():
        print(f"[跳过] {t} 不存在")
        continue

    data = json.loads(t.read_text(encoding="utf-8"))
    secs = data.get("qcStandard", {}).get("sections", [])
    changed = 0

    for s in secs:
        if str(s.get("n")) == "十五":
            old = list(s.get("items") or [])
            new = [x for x in old if x not in DROP]
            s["items"] = new
            changed = len(old) - len(new)
            print(f"十五节：{len(old)} → {len(new)} 项（删 {changed} 项）")
            print(f"  删除：{sorted(DROP & set(old))}")
            break

    if changed:
        bak = t.with_suffix(".json.bak_drop3")
        if not bak.exists():
            shutil.copy(t, bak)
            print(f"已备份：{bak.name}")
        t.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
        print(f"✔ 已写回：{t}")
    else:
        print(f"[无需改] {t}")