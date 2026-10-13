from pathlib import Path
import json

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
p09 = proj_root / "01_规划" / "全书结构"

print("=" * 70)
print("P09 产出检查")
print("=" * 70)

#  versions 目录 
versions = p09 / "versions"
if versions.exists():
    for ai_dir in sorted(versions.iterdir()):
        if ai_dir.is_dir():
            files = list(ai_dir.glob("*"))
            print(f"\n📁 {ai_dir.name}/  ({len(files)} 文件)")
            for f in files:
                size = f.stat().st_size
                print(f"   📄 {f.name}  ({size}B)")
                if f.suffix == ".md" and size > 0:
                    txt = f.read_text(encoding="utf-8", errors="ignore")
                    # 检查有无 JSON 块
                    has_json = "```json" in txt
                    print(f"      含 JSON 代码块：{'✅' if has_json else '❌'}")
                    print(f"      前 200 字：{txt[:200]}")
else:
    print("❌ versions 目录不存在")

#  split.json 
split = p09 / "split.json"
if split.exists():
    print(f"\n{'='*70}")
    print(f"✅ split.json 存在（{split.stat().st_size}B）")
    print(f"{'='*70}")
    data = json.loads(split.read_text(encoding="utf-8"))
    items = data.get("列表") or []
    print(f"  拆分维度：{data.get('拆分维度')}")
    print(f"  列表项数：{len(items)}")
    for it in items:
        print(f"     {it.get('key')}  {it.get('name')}  {it.get('start')}-{it.get('end')}  {it.get('note', '')[:30]}")
else:
    print(f"\n❌ split.json 不存在")

#  _failed 
failed = proj_root / "_failed"
if failed.exists():
    print(f"\n⚠️ _failed/ 存在：")
    for f in failed.rglob("*.json"):
        print(f"   {f.relative_to(failed)}")
else:
    print(f"\n✅ 无 _failed/")
