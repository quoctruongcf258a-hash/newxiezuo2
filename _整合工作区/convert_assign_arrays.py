# convert_assign_arrays.py — 把 assignments.json 的执行/审核/调整 从单值改数组
# 说明：
#   · 环节级：单值 "Doubao" → 数组 ["Doubao"]
#   · 明细级：如果原来没有这三字段，就继承环节级的值（打包成数组）
#   · 明细级：如果原来有，也转成数组
#   · 自动备份为 .bak_arrays
import json
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\rules\assignments.json")


def to_list(v):
    if v is None or v == "":
        return []
    if isinstance(v, list):
        return v
    return [v]


def main():
    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    bak = TARGET.with_suffix(".json.bak_arrays")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"✔ 已备份 → {bak.name}")

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    stage_changes = 0
    sub_changes = 0

    for stage_key, stage in data.get("环节", {}).items():
        print(f"\n【{stage_key}】")

        # 环节级三字段转数组
        for role in ("执行", "审核", "调整"):
            if role in stage:
                old = stage[role]
                new = to_list(old)
                if old != new:
                    stage[role] = new
                    stage_changes += 1
                    print(f"  [环节级] {role}: {old!r} → {new!r}")
            else:
                stage[role] = []
                stage_changes += 1
                print(f"  [环节级] {role}: 缺失 → []")

        stage_exec = stage.get("执行", [])
        stage_audit = stage.get("审核", [])
        stage_adj = stage.get("调整", [])

        # 明细级三字段
        detail = stage.get("明细", {})
        for sub_key, sub in detail.items():
            for role, inherited in (
                ("执行", stage_exec),
                ("审核", stage_audit),
                ("调整", stage_adj),
            ):
                if role in sub:
                    old = sub[role]
                    new = to_list(old)
                    if old != new:
                        sub[role] = new
                        sub_changes += 1
                        print(f"  [明细] {sub_key} / {role}: {old!r} → {new!r}")
                else:
                    sub[role] = list(inherited)
                    sub_changes += 1
                    print(f"  [明细] {sub_key} / {role}: 继承 → {sub[role]!r}")

    TARGET.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n✔ 已写回 {TARGET}")
    print(f"  环节级改动：{stage_changes} 处")
    print(f"  明细级改动：{sub_changes} 处")


if __name__ == "__main__":
    main()