# check_rings_mode.py — 打印 50 环的 mode 分布，一屏看清
import json
import os

BASE = r"F:\赛马23环整合工作室\程序2改装版"
RULES = os.path.join(BASE, "rules")
RINGS_JSON = os.path.join(RULES, "rings_items.json")
ASSIGN_JSON = os.path.join(RULES, "assignments.json")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    rings = load(RINGS_JSON)
    assign = load(ASSIGN_JSON)

    # 从 assignments 取 mode 的兜底表
    a_mode = {}
    for st, node in (assign.get("环节", {}) or {}).items():
        for name, v in (node.get("明细", {}) or {}).items():
            a_mode[(st, name)] = (v.get("mode") or "").strip()

    total = {"mesh": 0, "human": 0, "lock": 0, "storage": 0, "fixed": 0, "none": 0}

    print("=" * 78)
    print(f"项目：{rings.get('项目名', '?')}  章节数：{rings.get('章节数', '?')}")
    print("=" * 78)

    for 阶段 in ("01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"):
        info = rings.get(阶段, {})
        环节 = info.get("环节", [])
        print(f"\n【{阶段}】{len(环节)} 环")
        print("-" * 78)
        for item in 环节:
            code = item.get("code") or ""
            name = item.get("name") or ""
            typ = item.get("type", "")
            # 判定 mode
            if typ and typ != "fixed":
                mode = typ
            else:
                mode = a_mode.get((阶段, name), "") or a_mode.get((阶段, code), "")
                if not mode:
                    mode = "mesh"   # 兜底
            total[mode] = total.get(mode, 0) + 1
            tag = {"mesh": "M", "human": "H", "lock": "L",
                   "storage": "S", "fixed": "-", "none": "?"}.get(mode, "?")
            print(f"  [{tag}] {code:<12} {name:<24} {mode}")

    print("\n" + "=" * 78)
    总计 = sum(v for k, v in total.items() if k != "fixed")
    print(f"合计 {总计} 环")
    print(f"  mesh    : {total['mesh']}")
    print(f"  human   : {total['human']}")
    print(f"  lock    : {total['lock']}")
    print(f"  storage : {total['storage']}")
    print(f"  none    : {total['none']}")
    print("=" * 78)


if __name__ == "__main__":
    main()