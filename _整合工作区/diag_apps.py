import json
from pathlib import Path

root = Path(r"F:\赛马23环整合工作室\程序2改装版")
ap = root / "windows-use" / "apps.json"
data = json.loads(ap.read_text(encoding="utf-8"))

# ── 1. apps 数组（所有注册的 AI）──
print("=" * 70)
print("① apps 数组（注册的所有 AI）")
print("=" * 70)
for a in data.get("apps", []):
    if isinstance(a, dict):
        print(f"  key={a.get('key'):14} label={a.get('label', ''):14} cdpPort={a.get('cdpPort')}")

# ── 2. selected ──
print("\n" + "=" * 70)
print("② selected（当前选中）")
print("=" * 70)
print(f"  {data.get('selected')}")

# ── 3. rosterFile ──
print("\n" + "=" * 70)
print("③ rosterFile 指向")
print("=" * 70)
rf = data.get("rosterFile")
print(f"  rosterFile = {rf}")
if rf:
    rf_path = root / "windows-use" / rf if not Path(rf).is_absolute() else Path(rf)
    if rf_path.exists():
        print(f"  ✅ 文件存在：{rf_path}")
        try:
            rdata = json.loads(rf_path.read_text(encoding="utf-8"))
            print(f"  内容：{json.dumps(rdata, ensure_ascii=False, indent=2)[:1000]}")
        except Exception:
            print(f"  内容（原始）：{rf_path.read_text(encoding='utf-8')[:1000]}")
    else:
        print(f"  ❌ 文件不存在")
        # 尝试搜索
        for p in (root / "windows-use").rglob(Path(rf).name):
            print(f"     可能位置：{p}")

# ── 4. merge_app ──
print("\n" + "=" * 70)
print("④ merge_app（拼接者）")
print("=" * 70)
print(f"  {data.get('merge_app')}")

# ── 5. session_mod 相关文件 ──
print("\n" + "=" * 70)
print("⑤ session 模块相关文件")
print("=" * 70)
for p in (root / "windows-use").rglob("session*.py"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    print(f"  {p.relative_to(root)}")
for p in (root / "windows-use").rglob("roster*.json"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    print(f"  {p.relative_to(root)}")
for p in (root / "windows-use").rglob("today*.json"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    print(f"  {p.relative_to(root)}")
