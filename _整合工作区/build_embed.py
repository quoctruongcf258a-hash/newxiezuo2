# -*- coding: utf-8 -*-
"""
把第一版 37 环机制真正「嵌入」32流程版的执行链路。

三件事：
  A. 给 assignments.json 每个环补跨厂 writers / judges / merger
     （此前明细只有 mode/审核独立/audit，没有具体写手，赛马无从执行）
  B. 生成 prompts/<阶段>/<环名>.md 模板
     （此前 37 环缺 45 个模板，run_subphase 遇模板缺失会直接跳过 → 一环都跑不了）
  C. 生成 prompts/<阶段>/_通用.md 兜底模板

只改 F 盘副本：F:\\赛马23环整合工作室\\程序2改装版\\
"""
import json
import os

BASE = r"F:\赛马23环整合工作室\程序2改装版"
RULES = os.path.join(BASE, "rules")
PROMPTS = os.path.join(BASE, "prompts")

# 跨厂写手：5 家不同厂商（赛马 N 写手）
WRITERS = ["豆包", "通义千问", "DeepSeek", "Kimi", "腾讯元宝"]
# 跨厂裁判：与写手不同厂商，避免同源偏置（设计源铁律：盲审必须跨厂）
JUDGES = ["智谱清言", "文心一言", "讯飞星火"]
MERGER = "豆包"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f) or {}


def save(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def main():
    apath = os.path.join(RULES, "assignments.json")
    ppath = os.path.join(RULES, "phases.json")
    a = load(apath)
    p = load(ppath)

    # 备份
    for src in (apath, ppath):
        bk = src + ".bak_embed"
        if not os.path.exists(bk):
            save(bk, load(src))

    # 设计源描述（用于生成模板正文）：优先从 phases 条目取 desc
    desc_map = {}
    for st, subs in p.get("环节", {}).items():
        for s in subs:
            if isinstance(s, dict):
                desc_map[(st, s.get("name"))] = s.get("desc", "")

    stats = {"mesh": 0, "human": 0, "lock": 0, "none": 0}
    made_tpl = 0
    exists_tpl = 0

    for st, node in a.get("环节", {}).items():
        det = node.get("明细", {})
        for ring, v in det.items():
            mode = (v.get("mode") or "").strip()
            stats[mode if mode in stats else "none"] += 1

            # A. 补写手/裁判/汇总者
            if mode == "mesh":
                v["writers"] = v.get("writers") or WRITERS
                v["judges"] = v.get("judges") or JUDGES
                v["merger"] = v.get("merger") or MERGER
            elif mode == "human":
                v["writers"] = v.get("writers") or WRITERS[:1]
                v["judges"] = v.get("judges") or JUDGES[:1]
                v["merger"] = v.get("merger") or MERGER
            elif mode == "lock":
                v["writers"] = v.get("writers") or WRITERS[:1]
                v["judges"] = v.get("judges") or JUDGES[:1]
                v["merger"] = v.get("merger") or MERGER

            # B. 生成模板
            tdir = os.path.join(PROMPTS, st)
            os.makedirs(tdir, exist_ok=True)
            tpath = os.path.join(tdir, ring + ".md")
            if os.path.exists(tpath) and os.path.getsize(tpath) > 0:
                exists_tpl += 1
                continue
            desc = desc_map.get((st, ring), "") or v.get("desc", "")
            audit = v.get("audit") or []
            audit_txt = "\n".join("- " + str(x) for x in audit) if audit else "- 按本环节质量标准执行"
            body = f"""# 任务：{st} / {ring}

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
            with open(tpath, "w", encoding="utf-8") as f:
                f.write(body)
            made_tpl += 1

    # C. 各阶段 _通用.md 兜底
    for st in p.get("环节", {}).keys():
        tdir = os.path.join(PROMPTS, st)
        os.makedirs(tdir, exist_ok=True)
        g = os.path.join(tdir, "_通用.md")
        if not os.path.exists(g):
            with open(g, "w", encoding="utf-8") as f:
                f.write(f"""# 通用任务模板（{st}）

## 输入
{{{{输入}}}}

## 平台规则
{{{{平台规则}}}}

## 产物目录
{{{{产物目录}}}}

## 要求
按所属环节标准完成任务，输出完整成稿。
""")

    save(apath, a)

    print("=== A. 写手指派 ===")
    print(f"  补 writers/judges/merger；mode 分布 = {stats}")
    print(f"  写手(跨厂5家) = {WRITERS}")
    print(f"  裁判(跨厂3家) = {JUDGES}")
    print(f"  汇总者         = {MERGER}")
    print("\n=== B. prompt 模板 ===")
    print(f"  新建 = {made_tpl}   已存在保留 = {exists_tpl}")
    print("\n=== C. 兜底模板 ===")
    for st in p.get("环节", {}).keys():
        print(f"  prompts/{st}/_通用.md")


if __name__ == "__main__":
    main()
