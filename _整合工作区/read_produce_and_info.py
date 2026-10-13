from pathlib import Path

# ── 1. 读 do_produce 完整函数 ──
target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()

print("=== 定位 def do_produce ===")
for i, ln in enumerate(lines):
    if ln.strip().startswith("def do_produce"):
        print(f"=== 第 {i+1} 行：{ln.strip()} ===")
        end = i + 1
        while end < len(lines) and end < i + 200:
            if end > i + 1 and lines[end].startswith("def "):
                break
            end += 1
        for j in range(i, end):
            print(f"{j+1:4d}| {lines[j]}")
        print(f"\n=== 函数长度：{end - i} 行 ===")
        break
else:
    print("❌ 找不到 do_produce")

# ── 2. 找项目信息.json ──
print("\n=== 搜索 项目信息.json ===")
for p in Path(r"F:\赛马23环整合工作室").rglob("项目信息.json"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    print(f"  找到：{p}")
    try:
        import json
        data = json.loads(p.read_text(encoding="utf-8"))
        print(f"  顶层键：{list(data.keys())[:15]}")
        # 找人物设计列表
        for k, v in data.items():
            if "人物" in k:
                print(f"  {k}: {v}")
    except Exception as e:
        print(f"  读取失败：{e}")
