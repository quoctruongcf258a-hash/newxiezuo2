import sys, json
from pathlib import Path

root = Path(r"F:\赛马23环整合工作室\程序2改装版")
sys_path = root / "windows-use"

print("=" * 70)
print("① 找 participants / session 相关配置")
print("=" * 70)

# 候选配置文件
candidates = [
    root / "rules" / "apps.json",
    root / "windows-use" / "apps.json",
    root / "windows-use" / "_scratch" / "session.json",
    root / "windows-use" / "_scratch" / "participants.json",
    root / "windows-use" / "_scratch" / "stage_board.json",
]
for c in candidates:
    if c.exists():
        print(f"\n📄 {c}  ({c.stat().st_size}B)")
        try:
            data = json.loads(c.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                print(f"   顶层键：{list(data.keys())[:15]}")
            elif isinstance(data, list):
                print(f"   列表 {len(data)} 项")
                for item in data[:8]:
                    if isinstance(item, dict):
                        print(f"     {item.get('key')}: {item.get('label')} cdpPort={item.get('cdpPort')}")
        except Exception as e:
            print(f"   读失败：{e}")
    else:
        print(f"  ❌ 不存在：{c}")

print()
print("=" * 70)
print("② 搜索 orchestrator.py 里 participants 怎么加载")
print("=" * 70)
orch = sys_path / "_scratch" / "orchestrator.py"
lines = orch.read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(lines):
    if "participants" in ln and "=" in ln and "sess[" not in ln:
        # 找赋值语句
        print(f"  {i+1:4d}| {ln.strip()}")

print()
print("=" * 70)
print("③ 搜索 main 里怎么构造 sess")
print("=" * 70)
in_main = False
for i, ln in enumerate(lines):
    if ln.startswith("def main()"):
        in_main = True
        continue
    if in_main:
        if ln.startswith("def ") and not ln.startswith("def main"):
            break
        if "sess" in ln or "participants" in ln:
            print(f"  {i+1:4d}| {ln.strip()}")
