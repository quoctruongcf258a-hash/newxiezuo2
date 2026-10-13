# clean_prompts.py — 精确清理：只保留 rings_items.json 里列出的 code.md
import json
import os
import shutil

BASE = r"F:\赛马23环整合工作室\程序2改装版"
RULES = os.path.join(BASE, "rules")
PROMPTS = os.path.join(BASE, "prompts")
RINGS_JSON = os.path.join(RULES, "rings_items.json")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 60)
    print("clean_prompts — 精确清理模板")
    print("=" * 60)

    rings = load(RINGS_JSON)

    for 阶段 in ("01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"):
        info = rings.get(阶段, {})
        keep = set()
        for item in info.get("环节", []):
            code = item.get("code")
            if code:
                keep.add(code + ".md")
            name = item.get("name")
            if name:
                keep.add(name + ".md")   # 兼容 name 命名
        keep.add("_通用.md")

        tdir = os.path.join(PROMPTS, 阶段)
        if not os.path.isdir(tdir):
            print(f"[跳过] {阶段} 目录不存在")
            continue

        trash = os.path.join(tdir, "_trash")
        os.makedirs(trash, exist_ok=True)

        moved = 0
        kept = 0
        for f in sorted(os.listdir(tdir)):
            full = os.path.join(tdir, f)
            if os.path.isdir(full):
                continue
            if not f.endswith(".md"):
                continue
            if f in keep:
                kept += 1
            else:
                shutil.move(full, os.path.join(trash, f))
                moved += 1

        print(f"  {阶段:<10} 保留 {kept:>3}  移走 {moved:>3}  期望 {len(keep)}")

    print("\n完成。重跑：")
    print("  python build_embed_v2.py")


if __name__ == "__main__":
    main()