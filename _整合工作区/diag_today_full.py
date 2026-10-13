import json
from pathlib import Path

root = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use")

for f in [root / "today.json", root / "_scratch" / "today.json"]:
    if not f.exists():
        print(f"❌ 不存在：{f}")
        continue
    print("=" * 70)
    print(f"📄 {f}")
    print("=" * 70)
    data = json.loads(f.read_text(encoding="utf-8"))
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print()
