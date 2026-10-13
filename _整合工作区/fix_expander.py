# fix_expander.py — 重写 project_expander.py 的组装逻辑（新模板结构）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\project_expander.py")

NEW_CODE = '''# project_expander.py — 按项目信息动态展开 01_规划 的环节清单
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES_DIR = HERE.parent / "rules"
模板文件 = RULES_DIR / "环节模板.json"
phases文件 = RULES_DIR / "phases.json"
输出文件 = RULES_DIR / "rings_items.json"


def 读_json(p: Path, default=None):
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[错误] 读 {p} 失败：{e}")
        return default


def 读项目信息(项目目录: Path) -> dict:
    p = 项目目录 / "00_初始化" / "项目信息.json"
    if not p.exists():
        print(f"[错误] 找不到 {p}")
        sys.exit(1)
    return 读_json(p) or {}


def 计算外围环数(章节数: int, cfg: dict) -> int:
    base = int(cfg.get("基础数", 3))
    step = int(cfg.get("步长", 100))
    add = int(cfg.get("每步追加", 3))
    if 章节数 <= 0:
        return base
    return base + max(0, (章节数 - 1) // step) * add


def 展开外围环(章节数: int, cfg: dict) -> list:
    n = 计算外围环数(章节数, cfg)
    pool = cfg.get("环池", [])
    out = []
    for item in pool[:n]:
        out.append({
            "code": item["code"],
            "name": item["name"],
            "type": "peripheral",
            "desc": item["desc"],
        })
    return out


def 组装规划环节(模板: dict, 项目信息: dict) -> dict:
    固定环 = 模板.get("固定环", [])
    外围cfg = 模板.get("外围设计环", {})
    章节数 = int(项目信息.get("章节数") or 100)

    外围环 = 展开外围环(章节数, 外围cfg)

    结果 = []
    for r in 固定环:
        item = {**r, "type": "fixed"}
        # 保留 segment_mode / segment_size
        if r.get("segment_mode"):
            item["segment_mode"] = r["segment_mode"]
        if r.get("segment_size"):
            item["segment_size"] = r["segment_size"]
        结果.append(item)
        # 在 P08 之后插入外围环
        if r["code"] == "P08":
            结果.extend(外围环)

    return {
        "环数": len(结果),
        "固定环数": sum(1 for x in 结果 if x["type"] == "fixed"),
        "外围环数": len(外围环),
        "章节数": 章节数,
        "环节": 结果,
    }


def 抄其他阶段(phases: dict) -> dict:
    环节 = phases.get("环节", {}) or {}
    out = {}
    for 阶段 in ("02_写作", "03_去AI", "04_审核", "05_出厂"):
        items = 环节.get(阶段, [])
        norm = []
        for i, item in enumerate(items, 1):
            if isinstance(item, str):
                norm.append({"code": f"{阶段[:2]}-{i:02d}", "name": item, "type": "fixed"})
            elif isinstance(item, dict):
                norm.append({
                    "code": item.get("code") or f"{阶段[:2]}-{i:02d}",
                    "name": item.get("name", ""),
                    "type": item.get("mode", "fixed"),
                    "raw": item,
                })
        out[阶段] = {"环数": len(norm), "环节": norm}
    return out


def 生成(项目信息: dict, 模板: dict, phases: dict) -> dict:
    return {
        "_说明": "本次项目专属的完整环节清单，由 project_expander.py 生成。",
        "生成时间": time.strftime("%Y-%m-%d %H:%M:%S"),
        "项目名": 项目信息.get("项目名称") or 项目信息.get("name") or "未命名",
        "章节数": int(项目信息.get("章节数") or 100),
        "01_规划": 组装规划环节(模板, 项目信息),
        **抄其他阶段(phases),
    }


def 打印摘要(清单: dict):
    print("=" * 70)
    print(f"项目：{清单['项目名']}　章节数：{清单['章节数']}")
    print("=" * 70)
    g = 清单["01_规划"]
    print(f"01_规划：总 {g['环数']} 环 （固定 {g['固定环数']} + 外围 {g['外围环数']}）")
    print()
    for r in g["环节"]:
        mark = {"fixed": "  ", "peripheral": "🌐"}.get(r["type"], "  ")
        seg = ""
        if r.get("segment_mode"):
            seg = f"  [{r['segment_mode']}]"
        print(f"  {mark} {r['code']:<8} {r['name']}{seg}")
    print()
    for 阶段 in ("02_写作", "03_去AI", "04_审核", "05_出厂"):
        info = 清单[阶段]
        print(f"{阶段}：{info['环数']} 环")
    print()
    print(f"合计：{g['环数'] + sum(清单[s]['环数'] for s in ('02_写作','03_去AI','04_审核','05_出厂'))} 个环节")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-dir", default="")
    ap.add_argument("--info", default="")
    ap.add_argument("--out", default=str(输出文件))
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    模板 = 读_json(模板文件)
    if not 模板:
        print(f"[错误] 找不到 {模板文件}")
        sys.exit(1)
    phases = 读_json(phases文件, default={"环节": {}})

    if args.demo:
        项目信息 = {"项目名称": "示例", "章节数": 200}
    elif args.info:
        项目信息 = 读_json(Path(args.info)) or {}
    elif args.project_dir:
        项目信息 = 读项目信息(Path(args.project_dir))
    else:
        print("[错误] 请给 --project-dir 或 --info 或 --demo")
        sys.exit(1)

    清单 = 生成(项目信息, 模板, phases)
    打印摘要(清单)

    if args.demo:
        print("\\n[demo] 未写盘。")
        return

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(清单, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"\\n✔ 已写入：{out}")


if __name__ == "__main__":
    main()
'''

if TARGET.exists():
    bak = TARGET.with_suffix(".py.bak_expander2")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

TARGET.write_text(NEW_CODE, encoding="utf-8")
print(f"✔ 已重写 {TARGET}")