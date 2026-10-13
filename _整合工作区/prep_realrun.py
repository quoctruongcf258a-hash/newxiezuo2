import json, shutil
from pathlib import Path

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")

# 1. 备份粗纲规划的 split.json
p15_split = proj_root / "01_规划" / "粗纲规划" / "split.json"
bak = p15_split.with_suffix(".json.bak_realrun")
if not bak.exists():
    shutil.copy(p15_split, bak)
    print(f"已备份：{bak.name}")

# 2. 改成只含 1-3 章
data = json.loads(bak.read_text(encoding="utf-8"))
orig_items = data.get("列表") or []
print(f"原始：{len(orig_items)} 章")

data["列表"] = orig_items[:3]  # 只取前 3
print(f"现在：{len(data['列表'])} 章")

p15_split.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已写回 split.json")

# 3. 清空 W0 的旧产出
w0_dir = proj_root / "02_写作" / "W0_细纲分析"
for sub in ["versions", "reviews", "merged"]:
    p = w0_dir / sub
    if p.exists():
        shutil.rmtree(p)
        print(f"已清空：{p.relative_to(proj_root)}")

# 4. 清空 _failed
failed = proj_root / "_failed"
if failed.exists():
    shutil.rmtree(failed)
    print(f"已清空：_failed/")

print("\n=== 准备完成，可以真跑了 ===")
