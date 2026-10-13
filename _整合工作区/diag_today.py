import json
from pathlib import Path

root = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use")

print("=" * 70)
print("① today.json（根目录）")
print("=" * 70)
for f in [root / "today.json", root / "_scratch" / "today.json"]:
    if f.exists():
        print(f"\n📄 {f}")
        print(f"  大小：{f.stat().st_size}B")
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        except Exception as e:
            print(f"  读失败：{e}")

print()
print("=" * 70)
print("② apps.json 的 apps 字段类型")
print("=" * 70)
ap = root / "apps.json"
data = json.loads(ap.read_text(encoding="utf-8"))
apps = data.get("apps")
print(f"  apps 类型：{type(apps)}")
if isinstance(apps, dict):
    for k, v in apps.items():
        if isinstance(v, dict):
            print(f"  {k}: label={v.get('label', ''):14} cdpPort={v.get('cdpPort')} exe={str(v.get('exe', ''))[:40]}")
elif isinstance(apps, list):
    for a in apps:
        print(f"  {a}")

print()
print("=" * 70)
print("③ session.py 里 load_today / resolve / load_roster")
print("=" * 70)
sp = root / "_scratch" / "session.py"
if sp.exists():
    lines = sp.read_text(encoding="utf-8").splitlines()
    for target in ["def load_today", "def load_roster", "def resolve"]:
        i_f = None
        for i, ln in enumerate(lines):
            if ln.startswith(target):
                i_f = i
                break
        if i_f is None:
            print(f"  ❌ 找不到 {target}")
            continue
        print(f"\n=== {target} (第 {i_f+1} 行) ===")
        end = i_f + 1
        while end < len(lines) and end < i_f + 60:
            if end > i_f + 1 and lines[end].startswith("def "):
                break
            end += 1
        for j in range(i_f, end):
            print(f"  {j+1:4d}| {lines[j]}")
