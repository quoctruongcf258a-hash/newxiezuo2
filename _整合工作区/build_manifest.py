# -*- coding: utf-8 -*-
"""
任务 A：把第一版 23 环规划设计 + 八方向审核，从原始 apps.json 抽取成
一份干净、可机读、程序2（协同写作）可直接加载的「运行清单 manifest」。

产物：manifest_23环_整合.json
  - meta          来源/版本/日期/说明
  - phases        23 个规划环（key/mode/stage/supp/desc/subitems/gateHooks/audit）
  - auditDirections 八方向质量闸门（rings/extends/questions/standards/failPatterns）
  - qualityGates  写作/润色/质检 三道闸门的引用指针（sixElements/polishStandard/qcStandard）
  - roleModel     三阶段角色模型（执行/审核/调整）+ 赛马独立把关规则
  - integration   程序2 应如何消费本清单（替换其 rules/phases.json 的 01_规划）
"""
import json, re, os, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "..", "_backup_第一版23环设计", "协同层", "配置", "apps.json")
OUT = os.path.join(BASE, "manifest_23环_整合.json")

d = json.load(open(SRC, encoding="utf-8"))
phases = d["phases"]
audit = d["auditDirections"]

# ---- 1) 抽取 23 个规划环（phases[0:23]）----
PLAN_START, PLAN_END = 0, 23
plan = phases[PLAN_START:PLAN_END]

def parse_subitems(desc):
    """从 desc 里解析 'X子项' 这类明确数字；拿不到返回 None。"""
    if not desc:
        return None
    m = re.search(r"(\d+)\s*子项", desc)
    if m:
        return int(m.group(1))
    return None

# 设计文档中明确给出、但 desc 未写 'X子项' 字样的已知子项数（来自赛马全流程.md / 52-程序一文档）
KNOWN_SUBITEMS = {
    "结局与终局": 8,        # 终局画面/主角终态/世界变化/最大代价/反派结局/配角结局/主题回答/最后场景
}

clean_phases = []
for i, p in enumerate(plan):
    gate_hooks = {k: p[k] for k in ("cross_cutting", "pack", "craft", "six", "polish", "qcSecs") if k in p}
    clean_phases.append({
        "id": i + 1,                      # 1..23 序位
        "key": p["key"],                  # 环节名（如「主角设计」）
        "mode": p["mode"],                # mesh / human / lock
        "stage": p.get("stage"),
        "supp": p.get("supp"),            # 是否支持（被后续环引用）
        "desc": p.get("desc", ""),
        "subitems": parse_subitems(p.get("desc", "")) or KNOWN_SUBITEMS.get(p["key"]),  # 明确子项数 or 已知 or None
        "gateHooks": gate_hooks,          # 该环挂载的其它闸门钩子
    })

# ---- 2) 八方向审核（干净化）----
clean_audit = []
for a in audit:
    clean_audit.append({
        "key": a.get("key"),
        "rings": a.get("rings", []),          # 主适用环
        "extends": a.get("extends", []),       # 扩展适用环（包装类）
        "questions": a.get("questions", []),
        "standards": a.get("standards", []),
        "failPatterns": a.get("failPatterns", []),
    })

# 为每个规划环标注「适用哪些八方向闸门」
ring_to_audit = {}
for idx, ph in enumerate(clean_phases):
    appl = []
    for ad in clean_audit:
        if ph["key"] in (ad["rings"] + ad["extends"]):
            appl.append(ad["key"])
    ph["audit"] = appl

# ---- 3) 质量闸门指针（写作/润色/质检）----
def _keys_or_len(node):
    """dict→keys 列表；list→长度；其它→None。"""
    if isinstance(node, dict):
        return list(node.keys())
    if isinstance(node, list):
        return len(node)
    return None

_six = d.get("sixElements") or {}
_pol = d.get("polishStandard") or {}
_qc = d.get("qcStandard") or {}
quality_gates = {
    "写作_六要素": {
        "source": "apps.json::sixElements",
        "auditFlag": d.get("sixAudit"),
        "desc": "章节循环按六要素拆 6 段分块产出；审核按 sixElements 六要素标准。",
        "elements_ref": _keys_or_len(_six.get("elements")) if isinstance(_six, dict) else None,
    },
    "润色_四节28子项": {
        "source": "apps.json::polishStandard",
        "desc": "前准备→常规润色→去AI味专项→朗读试读；出口经润色终审。",
        "sections": _keys_or_len(_pol.get("sections")) if isinstance(_pol, dict) else None,
    },
    "质检_多维度": {
        "source": "apps.json::qcStandard",
        "desc": "逻辑设定一致/平台合规/爽点节奏/文风格式回查/质检汇总/成书检验。",
        "sections": _keys_or_len(_qc.get("sections")) if isinstance(_qc, dict) else None,
    },
}

# ---- 4) 三阶段角色模型（修复「审核=执行同AI」问题）----
role_model = {
    "说明": "每个规划环走 执行→审核→调整 三角色闭环；mesh 环的审核必须是"
            "跨厂独立盲审（审核者≠执行写手），human 环审核归人，lock 环 AI 审计+人锁。",
    "mesh": {
        "执行": "N 个写手各写 1 份（全网格赛马）",
        "审核": "盲审：每写手审另外 N-1 份，跨厂独立裁判，计数取冠军",
        "调整": "汇总者按块择优 / 融合定稿",
        "硬规则": "审核者集合与执行写手集合无交集（跨厂选裁判，杜绝同源偏置）",
    },
    "human": {
        "执行": "AI 出模板/候选选项",
        "审核": "人拍板（人定）",
        "调整": "人定稿",
    },
    "lock": {
        "执行": "AI 跑方向级审计 + 清单/依赖/一致性",
        "审核": "AI 审计（八方向逐方向打勾）",
        "调整": "人终检锁章纲",
    },
}

# ---- 5) 整合指引（程序2 如何消费）----
integration = {
    "目标": "用本清单替换程序2 rules/phases.json 的「01_规划」（原仅 7 粗子环 1.1-1.7），"
            "升级其「审核」为八方向独立闸门，保留程序2 的写作/去AI/审核/出厂产能。",
    "替换映射": {
        "程序2 原 01_规划 7 子环": ["1.0_总纲复核","1.1_定位与卖点复核","1.2_故事核心主题复核",
                              "1.3_人物系统复核","1.4_世界观与设定复核","1.5_结构与节奏复核","1.6_卷纲复核"],
        "对应本清单 23 环": "规划前约束→类型平台读者卖点→文风与叙事基调→一句话故事→简介与主题→"
                      "主角设计→核心冲突与反派→核心配角与人物关系→世界规则最小集→结局与终局→"
                      "分卷结构→情绪规划→节奏规划→前30章章纲→开篇黄金三章爆破→伏笔时间线关系表→"
                      "书名设计→上架简介→标签选择→封面设计规划→文档与备份→发布与合规→规划验收",
    },
    "审核升级": "程序2 assignments.json 里 01_规划 的「审核」不得再等于「执行」（如 1-1 三者同=WorkBuddy）；"
                "mesh 环审核改为「跨厂盲审投票」，human 环审核归人，lock 环人锁。",
    "闸门挂载": "每个规划环的 audit 字段列出它受哪些八方向闸门约束，审核时逐方向打勾。",
}

manifest = {
    "meta": {
        "name": "第一版赛马 23 环规划 × 八方向审核 · 整合运行清单",
        "version": "1.0",
        "generated": datetime.date.today().isoformat(),
        "source": "C:/.../协同层/配置/apps.json (备份于 F:/赛马23环整合工作室/_backup_第一版23环设计/)",
        "designDoc": "赛马全流程.md / 52-程序一-规划23环与八方向审核.md",
        "ringCount": len(clean_phases),
        "auditDirectionCount": len(clean_audit),
        "desc": "从第一版赛马设计抽出的干净运行清单：23 规划环 + 八方向质量闸门 + 三阶段角色模型，"
                "供程序2（协同写作）直接加载，取代其粗粒度 01_规划。",
    },
    "phases": clean_phases,
    "auditDirections": clean_audit,
    "qualityGates": quality_gates,
    "roleModel": role_model,
    "integration": integration,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

# ---- 打印摘要 ----
print("✅ 清单已生成:", OUT)
print("   规划环数:", len(clean_phases))
print("   八方向数:", len(clean_audit))
modes = {}
for p in clean_phases:
    modes[p["mode"]] = modes.get(p["mode"], 0) + 1
print("   模式分布:", modes)
print("   挂载子项数的环:", sum(1 for p in clean_phases if p["subitems"]))
# 每个八方向覆盖多少环
print("\n   八方向 → 覆盖环数:")
for ad in clean_audit:
    n = len(ad["rings"]) + len(ad["extends"])
    print(f"     {ad['key']:<8} 主{len(ad['rings'])} + 扩{len(ad['extends'])} = {n}")
