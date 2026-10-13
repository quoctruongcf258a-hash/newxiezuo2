# -*- coding: utf-8 -*-
"""
build_embed_v2.py — 修复缺口 2：模板注入 desc

数据源变更：
  旧：phases.json 的 desc（实际没有 desc 字段 → 全部落成"无额外说明"）
  新：优先 rings_items.json（本项目 50 环的专属 desc）
     补充 apps.json 的 phases[].desc（原版 37 环的通用 desc）

产出：
  · prompts/<阶段>/<环节名>.md —— 每个环节一个专属模板（覆盖旧的）
  · prompts/<阶段>/_通用.md —— 兜底
  · 可选：更新 assignments.json（补 writers/judges/merger）

只改 F 盘副本，原盘不动。
"""
import json
import os
import re

BASE = r"F:\赛马23环整合工作室\程序2改装版"
RULES = os.path.join(BASE, "rules")
PROMPTS = os.path.join(BASE, "prompts")
APPS_JSON = os.path.join(BASE, "windows-use", "_scratch", "apps.json")
RINGS_JSON = os.path.join(RULES, "rings_items.json")
PHASES_JSON = os.path.join(RULES, "phases.json")
ASSIGN_JSON = os.path.join(RULES, "assignments.json")

WRITERS = ["豆包", "通义千问", "DeepSeek", "Kimi", "腾讯元宝"]
JUDGES = ["智谱清言", "文心一言", "讯飞星火"]
MERGER = "豆包"


def load(p, default=None):
    if not os.path.exists(p):
        return default
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[错误] 读 {p} 失败：{e}")
        return default


def save(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


# ────────────────────────────────────────────────────────
# 构建 desc_map
# ────────────────────────────────────────────────────────

def build_apps_desc_map(apps):
    """从 apps.json 的 phases[].desc 构建 {环 key: desc}"""
    m = {}
    for ph in apps.get("phases", []):
        key = ph.get("key", "")
        desc = ph.get("desc", "")
        if key and desc:
            m[key] = desc
    return m


def match_apps_key(name, apps_map):
    """rings_items 的环节名 → apps.json 的 key（模糊匹配）"""
    if not name:
        return None
    # 1. 直接相等
    if name in apps_map:
        return name
    # 2. 去掉编号前缀（P01_ / P06-01 / W1_ / Q2_ / R1_ / P0Z-1_）
    stripped = re.sub(r'^(P\d+[-\d]*|W\d+|Q\d+|R\d+|P0Z[-\d]*)[_\-\s]+', '', name)
    stripped = stripped.strip()
    if stripped in apps_map:
        return stripped
    # 3. 人物设计-xxx → 主角设计
    if name.startswith("人物设计") or stripped.startswith("人物设计"):
        return "主角设计"
    # 4. 外围环 → 世界规则最小集
    for kw in ("门派", "势力", "副本", "任务线", "血脉", "灵兽",
               "地图", "秘境", "宝物", "传承", "天骄", "对手",
               "战争", "格局", "飞升", "世界层级"):
        if kw in name:
            return "世界规则最小集"
    return None


def build_desc_map(apps, rings):
    """合并 rings_items.json 的 desc 与 apps.json 的 desc"""
    apps_map = build_apps_desc_map(apps)
    out = {}   # (阶段, code) 或 (阶段, name) → desc
    命中_apps = 0
    命中_rings = 0
    缺失 = []

    for 阶段 in ("01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"):
        info = rings.get(阶段, {})
        for item in info.get("环节", []):
            code = item.get("code") or item.get("name", "")
            name = item.get("name", "")
            desc = (item.get("desc") or "").strip()

            if not desc:
                key = match_apps_key(name, apps_map)
                if key:
                    desc = apps_map[key]
                    命中_apps += 1
                else:
                    缺失.append(f"{阶段} / {code} {name}")

            if desc:
                out[(阶段, code)] = desc
                out[(阶段, name)] = desc
                if desc and not desc.startswith("（"):
                    命中_rings += 1

    return out, {
        "命中_apps": 命中_apps,
        "命中_rings": 命中_rings,
        "缺失": 缺失,
    }


# ────────────────────────────────────────────────────────
# 生成模板
# ────────────────────────────────────────────────────────

def make_template(阶段, code, name, desc, mode, audit_txt):
    body = f"""# 任务：{阶段} / {name}

**执行模式**：{mode or '标准三角色（执行→审核→调整）'}

## 环节说明
{desc or '（无额外说明，按本环节标准执行）'}

## 评审 / 审核标准
{audit_txt}

## 输入
{{{{输入}}}}

## 平台规则
{{{{平台规则}}}}

## 产物目录
{{{{产物目录}}}}

## 要求
1. 严格围绕本环节目标产出，不要越界写其他环节的内容。
2. 输出完整成稿，不要写"略"或占位。
3. 若输入为空，则依据上一步已确认的上下文自行合理推进，并在开头标注假设。
"""
    return body


def build_prompts(rings, desc_map, assignments):
    made = 0
    skipped = 0
    updated = 0

    a_rings = {}
    for st, node in (assignments.get("环节", {}) or {}).items():
        for ring_name, v in (node.get("明细", {}) or {}).items():
            a_rings[(st, ring_name)] = v

    for 阶段 in ("01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"):
        info = rings.get(阶段, {})
        tdir = os.path.join(PROMPTS, 阶段)
        os.makedirs(tdir, exist_ok=True)

        for item in info.get("环节", []):
            code = item.get("code") or item.get("name", "")
            name = item.get("name", "")

            # 文件名：优先 code（短、无中文、安全）
            fname = (code if code else name).replace("/", "_").replace("\\", "_")
            tpath = os.path.join(tdir, fname + ".md")

            desc = desc_map.get((阶段, code), "") or desc_map.get((阶段, name), "")
            mode = item.get("type", "") if item.get("type") not in ("fixed",) else ""
            if not mode:
                a = a_rings.get((阶段, name), {}) or a_rings.get((阶段, code), {})
                mode = a.get("mode", "")

            a = a_rings.get((阶段, name), {}) or a_rings.get((阶段, code), {})
            audit = a.get("audit") or []
            audit_txt = "\n".join("- " + str(x) for x in audit) if audit \
                else "- 按本环节质量标准执行"

            body = make_template(阶段, code, name, desc, mode, audit_txt)

            if os.path.exists(tpath):
                old = open(tpath, encoding="utf-8").read()
                if old == body:
                    skipped += 1
                    continue
                with open(tpath, "w", encoding="utf-8") as f:
                    f.write(body)
                updated += 1
            else:
                with open(tpath, "w", encoding="utf-8") as f:
                    f.write(body)
                made += 1

        # 兜底
        g = os.path.join(tdir, "_通用.md")
        if not os.path.exists(g):
            with open(g, "w", encoding="utf-8") as f:
                f.write(f"""# 通用任务模板（{阶段}）

## 输入
{{{{输入}}}}

## 平台规则
{{{{平台规则}}}}

## 产物目录
{{{{产物目录}}}}

## 要求
按所属环节标准完成任务，输出完整成稿。
""")

    return {"新建": made, "覆盖更新": updated, "无变化跳过": skipped}


# ────────────────────────────────────────────────────────
# 补 assignments
# ────────────────────────────────────────────────────────

def build_assignments(assignments, rings):
    stats = {"mesh": 0, "human": 0, "lock": 0, "none": 0}
    a_rings = assignments.setdefault("环节", {})

    for 阶段 in ("01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"):
        node = a_rings.setdefault(阶段, {"子环": [], "明细": {}})
        明细 = node.setdefault("明细", {})

        info = rings.get(阶段, {})
        for item in info.get("环节", []):
            name = item.get("name", "")
            if not name:
                continue
            if name not in 明细:
                明细[name] = {}
            v = 明细[name]
            mode = item.get("type", "") if item.get("type") != "fixed" else v.get("mode", "")
            if not mode:
                mode = v.get("mode", "mesh")
            v["mode"] = mode
            stats[mode if mode in stats else "none"] += 1

            if mode == "mesh":
                v.setdefault("writers", WRITERS)
                v.setdefault("judges", JUDGES)
                v.setdefault("merger", MERGER)
            elif mode in ("human", "lock"):
                v.setdefault("writers", WRITERS[:1])
                v.setdefault("judges", JUDGES[:1])
                v.setdefault("merger", MERGER)

        # 更新 子环 列表（保持顺序）
        node["子环"] = [x.get("name", "") for x in info.get("环节", []) if x.get("name")]

    return stats


# ────────────────────────────────────────────────────────
# 主流程
# ────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("build_embed_v2 — 修复缺口 2（desc 注入）")
    print("=" * 70)

    apps = load(APPS_JSON) or {}
    rings = load(RINGS_JSON)
    if not rings:
        print(f"[错误] 找不到 {RINGS_JSON}")
        print("  请先跑：python app/project_expander.py --project-dir <项目目录>")
        return
    assignments = load(ASSIGN_JSON) or {}

    print(f"\n【1】数据源")
    print(f"  rings_items.json：{rings.get('项目名', '?')} / {rings.get('章节数', '?')} 章")
    print(f"  apps.json：{len(apps.get('phases', []))} 个 phase")

    print(f"\n【2】构建 desc_map")
    desc_map, dstat = build_desc_map(apps, rings)
    print(f"  命中 apps.json：{dstat['命中_apps']}")
    print(f"  命中 rings 自带 desc：{dstat['命中_rings']}")
    print(f"  总条数：{len(desc_map)}")
    if dstat["缺失"]:
        print(f"  [警告] 缺失 desc：{len(dstat['缺失'])} 条")
        for m in dstat["缺失"][:10]:
            print(f"     - {m}")

    print(f"\n【3】生成模板")
    pstat = build_prompts(rings, desc_map, assignments)
    print(f"  新建：{pstat['新建']}")
    print(f"  覆盖更新：{pstat['覆盖更新']}")
    print(f"  无变化跳过：{pstat['无变化跳过']}")

    print(f"\n【4】补 assignments")
    for src in (ASSIGN_JSON,):
        bk = src + ".bak_v2"
        if not os.path.exists(bk):
            save(bk, load(src) or {})
            print(f"  已备份：{os.path.basename(bk)}")
    astat = build_assignments(assignments, rings)
    save(ASSIGN_JSON, assignments)
    print(f"  mode 分布：{astat}")

    print(f"\n【5】抽查验证")
    for 抽查 in ("01_规划",):
        tdir = os.path.join(PROMPTS, 抽查)
        files = sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []
        print(f"  {抽查}：{len(files)} 个模板")
        样例 = [f for f in files if "P06" in f or "人物设计" in f]
        if 样例:
            p = os.path.join(tdir, 样例[0])
            txt = open(p, encoding="utf-8").read()
            print(f"\n  ── 抽查 {样例[0]} ──")
            print("  " + txt.split("## 环节说明")[1].split("##")[0].strip()[:200])

    print(f"\n完成。")


if __name__ == "__main__":
    main()