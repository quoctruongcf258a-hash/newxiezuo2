import json
from pathlib import Path

rings = json.loads(Path(r"F:\赛马23环整合工作室\程序2改装版\rules\rings_items.json").read_text(encoding="utf-8"))

# 需要关注的关键词（提示这个环节需要任务拆分）
SPLIT_HINTS = ["按卷", "按章", "按段", "分次", "每卷", "每章", "每段",
               "分卷", "分段", "逐卷", "逐章", "逐段",
               "1-30章", "31-60章", "第一卷", "第二卷",
               "个人物", "每个人物", "每人一份", "独立文件"]

print("=== 审计：所有环节里，desc/name 含拆分提示的 ===")
print(f"（关键词：{SPLIT_HINTS}）\n")

for phase_key in ["01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"]:
    if phase_key not in rings:
        continue
    print(f"\n{'='*70}")
    print(f"📁 {phase_key}")
    print(f"{'='*70}")
    for ring in rings[phase_key].get("环节", []):
        code = ring.get("code", "?")
        name = ring.get("name", "?")
        desc = ring.get("desc", "")
        fields = ring.get("fields") or []

        # 检查是否命中拆分提示
        hits = [k for k in SPLIT_HINTS if k in desc or k in name]
        # 也检查 fields 里
        for f in fields:
            for k in SPLIT_HINTS:
                if k in str(f) and k not in hits:
                    hits.append(k)

        if hits:
            print(f"\n  ★ {code} {name}")
            print(f"    desc: {desc[:150]}")
            if fields:
                print(f"    fields: {fields}")
            print(f"    命中拆分提示：{hits}")
