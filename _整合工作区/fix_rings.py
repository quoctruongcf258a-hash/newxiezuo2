# fix_rings.py — 修两个问题
#   1) rings_items.json：把 6 个 human 环 + 1 个 lock 环的 type 改对
#   2) prompts/01_规划/：清理旧模板（非 P/W/Q/R 开头的中文名文件）
import json
import os
import re
import shutil

BASE = r"F:\赛马23环整合工作室\程序2改装版"
RULES = os.path.join(BASE, "rules")
PROMPTS = os.path.join(BASE, "prompts")
RINGS_JSON = os.path.join(RULES, "rings_items.json")

# 01_规划 里 6 个 human + 1 个 lock
MODE_OVERRIDE = {
    "P01": "human",   # 规划前约束
    "P02": "human",   # 类型平台读者卖点
    "P03": "human",   # 文风与叙事基调
    "P17": "human",   # 标签选择
    "P19": "human",   # 文档与备份
    "P20": "human",   # 发布与合规
    "P21": "lock",    # 规划验收
}


def load(p, default=None):
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def fix_rings():
    rings = load(RINGS_JSON)
    if not rings:
        print("[错误] rings_items.json 不存在")
        return
    n = 0
    for item in rings.get("01_规划", {}).get("环节", []):
        code = item.get("code", "")
        if code in MODE_OVERRIDE:
            old = item.get("type", "")
            item["type"] = MODE_OVERRIDE[code]
            print(f"  {code:<8} {item.get('name',''):<20} {old} → {MODE_OVERRIDE[code]}")
            n += 1
    save(RINGS_JSON, rings)
    print(f"✔ 修了 {n} 个环的 type")


def clean_prompts():
    tdir = os.path.join(PROMPTS, "01_规划")
    if not os.path.isdir(tdir):
        print(f"[跳过] {tdir} 不存在")
        return
    trash = os.path.join(tdir, "_trash")
    os.makedirs(trash, exist_ok=True)
    moved = 0
    kept = 0
    for f in sorted(os.listdir(tdir)):
        if not f.endswith(".md"):
            continue
        if f == "_通用.md":
            kept += 1
            continue
        # 保留 P/W/Q/R 开头的（新命名）
        if re.match(r"^[PWQR]", f):
            kept += 1
            continue
        shutil.move(os.path.join(tdir, f), os.path.join(trash, f))
        moved += 1
    print(f"✔ 保留 {kept} 个新模板，移走 {moved} 个旧模板到 _trash/")


def main():
    print("=" * 60)
    print("fix_rings — 修 human 环 type + 清理旧模板")
    print("=" * 60)
    print("\n【1】修 rings_items.json 的 type")
    fix_rings()
    print("\n【2】清理 prompts/01_规划/ 旧模板")
    clean_prompts()
    print("\n完成。下一步跑：")
    print("  python build_embed_v2.py")


if __name__ == "__main__":
    main()