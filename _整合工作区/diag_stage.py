from pathlib import Path
import json

print("=== 全盘搜索 进度.json ===")
found = []
for p in Path(r"F:\赛马23环整合工作室\程序2改装版\output").rglob("进度.json"):
    print(f"  找到: {p}")
    print(f"    大小: {p.stat().st_size}B")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        print(f"    当前阶段: {data.get('当前阶段')}")
        print(f"    阶段列表: {len(data.get('阶段列表') or [])} 项")
        for s in (data.get('阶段列表') or [])[:3]:
            print(f"      - 阶段{s.get('阶段号')}  {s.get('起章')}-{s.get('止章')}")
    except Exception as e:
        print(f"    解析失败: {e}")
    found.append(p)

if not found:
    print("  ❌ 全盘没有找到 进度.json！")

# 检查 P17/P18 环节的 out_dir 长什么样
print("\n=== P17 细纲的 out_dir ===")
p17_versions = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test\01_规划\细纲\versions")
print(f"  存在: {p17_versions.exists()}")
if p17_versions.exists():
    files = list(p17_versions.glob("*.md"))
    print(f"  文件数: {len(files)}")
    for f in sorted(files)[:5]:
        print(f"    {f.name}")

# 检查 fake P15 split.json
print("\n=== fake P15 split.json 现状 ===")
p15 = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test\01_规划\粗纲规划\split.json")
print(f"  存在: {p15.exists()}")
if p15.exists():
    d = json.loads(p15.read_text(encoding="utf-8"))
    items = d.get("列表") or []
    print(f"  列表项数: {len(items)}")
    for it in items[:3]:
        print(f"    {it}")
    print(f"    ...")
    for it in items[-2:]:
        print(f"    {it}")
