# fix_rings_mode.py — 把 person/peripheral 环的 type 改成 mesh，保留 kind 字段
import json
import os

BASE = r"F:\赛马23环整合工作室\程序2改装版"
RULES = os.path.join(BASE, "rules")
RINGS_JSON = os.path.join(RULES, "rings_items.json")
ASSIGN_JSON = os.path.join(RULES, "assignments.json")

MAP = {
    "person": "mesh",
    "peripheral": "mesh",
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
    n = 0
    for 阶段 in ("01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"):
        for item in rings.get(阶段, {}).get("环节", []):
            typ = item.get("type", "")
            if typ in MAP:
                item["kind"] = typ          # 保留原类型
                item["type"] = MAP[typ]     # 改成 mesh
                n += 1
    save(RINGS_JSON, rings)
    print(f"✔ rings_items.json：修了 {n} 环")


def fix_assign():
    a = load(ASSIGN_JSON, {}) or {}
    n = 0
    for st, node in (a.get("环节", {}) or {}).items():
        for name, v in (node.get("明细", {}) or {}).items():
            m = (v.get("mode") or "").strip()
            if m in MAP:
                v["kind"] = m
                v["mode"] = MAP[m]
                n += 1
    save(ASSIGN_JSON, a)
    print(f"✔ assignments.json：修了 {n} 条")


def main():
    print("=" * 60)
    print("fix_rings_mode — person/peripheral → mesh")
    print("=" * 60)
    fix_rings()
    fix_assign()
    print("\n完成。重跑：")
    print("  python build_embed_v2.py")
    print("  python check_rings_mode.py")


if __name__ == "__main__":
    main()