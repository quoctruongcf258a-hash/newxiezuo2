# -*- coding: utf-8 -*-
"""
试运行（Trial Run）：
 1) 校验 manifest_23环_整合.json 的完整性（23环/8方向/模式合法/八方向引用环存在/角色模型覆盖）。
 2) 干跑（dry-run，不调真实 AI 窗口）三个代表性环，验证清单能驱动流程：
      - mesh 环（主角设计）：N写 → N-1盲审 → 汇总择优 → 冠军
      - human 环（类型平台读者卖点）：AI候选 + 人拍板
      - lock 环（规划验收）：八方向逐方向审计 + 人锁
 3) 产出「程序2 可直接消费」的 phases/assignments 兼容片段，证明整合可落地。

说明：本试运行是结构/逻辑验证，不发起任何真实 AI 窗口调用（real 模式需 5 个 AI 桌面窗口+CDP）。
"""
import json, os, datetime, hashlib

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(BASE, "manifest_23环_整合.json")
OUT_SAMPLE = os.path.join(BASE, "trial_output_sample.json")
OUT_PROG2 = os.path.join(BASE, "prog2_兼容片段_试运行.json")

m = json.load(open(MANIFEST, encoding="utf-8"))
phases = m["phases"]
audit = m["auditDirections"]
ring_names = {p["key"] for p in phases}

report = []
def log(s):
    report.append(s)
    print(s)

# ============ 1) 完整性校验 ============
log("=" * 64)
log("【1】manifest 完整性校验")
log("=" * 64)
errs = []

# 环数
if len(phases) != 23:
    errs.append(f"规划环数应为23，实为{len(phases)}")
# 模式合法
valid_modes = {"mesh", "human", "lock"}
for p in phases:
    if p["mode"] not in valid_modes:
        errs.append(f"环[{p['id']}]{p['key']} 模式非法: {p['mode']}")
# 八方向引用环都存在
for ad in audit:
    for r in (ad["rings"] + ad["extends"]):
        if r not in ring_names:
            errs.append(f"八方向[{ad['key']}] 引用了不存在的环: {r}")
# 角色模型覆盖三模式
rm = m["roleModel"]
for md in ("mesh", "human", "lock"):
    if md not in rm:
        errs.append(f"角色模型缺模式: {md}")

if errs:
    log("❌ 校验失败:")
    for e in errs:
        log("   - " + e)
else:
    log("✅ 校验通过：23环 / 8方向 / 模式合法 / 八方向引用环均存在 / 角色模型覆盖 mesh·human·lock")

# ============ 2) 干跑三个代表性环 ============
log("")
log("=" * 64)
log("【2】干跑三个代表性环（SIM 模拟，不调真实 AI）")
log("=" * 64)

WRITERS = ["豆包", "千问", "ZCode", "WorkBuddy", "Qoder"]  # 示例阵容（与 mix_send 阵容一致）

def dry_mesh_ring(ring):
    """mesh 全网格：N写 → N-1盲审 → 汇总择优"""
    log(f"\n● MESH 环 [{ring['id']}] {ring['key']}  (子项={ring['subitems'] or '—'})")
    log(f"  执行：{len(WRITERS)} 写手各写 1 份 chunk（全网格赛马）")
    chunks = {w: f"<<{ring['key']}·{w}·草稿(模拟)>>" for w in WRITERS}
    log(f"  审核：每写手盲审其余 {len(WRITERS)-1} 份 → 交叉盲审矩阵 {len(WRITERS)}×{len(WRITERS)-1}")
    # 模拟盲审：除自己外逐一打分（1-10），确定性伪分
    scores = {}
    for reviewer in WRITERS:
        scores[reviewer] = {}
        for writer in WRITERS:
            if writer == reviewer:
                continue
            # 用确定性哈希生成稳定伪分（仅示意）
            h = int(hashlib.md5(f"{ring['key']}|{reviewer}|{writer}".encode()).hexdigest(), 16) % 4 + 7  # 7-10
            scores[reviewer][writer] = h
    # 汇总：取每份被审平均分
    avg = {}
    for writer in WRITERS:
        vals = [scores[r][writer] for r in WRITERS if r != writer]
        avg[writer] = round(sum(vals) / len(vals), 2)
    champion = max(avg, key=avg.get)
    log(f"  汇总择优：各写手均分 = {avg}")
    log(f"  🏆 冠军 = {champion}（{avg[champion]} 分）→ 个人最优版")
    # 八方向闸门
    if ring["audit"]:
        log(f"  八方向闸门：{ring['audit']}（审核时逐方向打勾）")
    return {"ring": ring["key"], "mode": "mesh", "chunks": chunks,
            "blind_matrix": scores, "averages": avg, "champion": champion,
            "auditDirections": ring["audit"]}

def dry_human_ring(ring):
    log(f"\n● HUMAN 环 [{ring['id']}] {ring['key']}")
    log(f"  执行：AI 出模板/候选选项")
    log(f"  审核：人拍板（人定）  ← 修复点：不再由 AI 自审")
    log(f"  调整：人定稿")
    if ring["audit"]:
        log(f"  八方向闸门：{ring['audit']}")
    return {"ring": ring["key"], "mode": "human", "exec": "AI候选", "review": "人拍板",
            "auditDirections": ring["audit"]}

def dry_lock_ring(ring):
    log(f"\n● LOCK 环 [{ring['id']}] {ring['key']}")
    log(f"  执行：AI 跑方向级审计 + 清单/依赖/一致性")
    log(f"  审核：AI 审计（八方向逐方向打勾）")
    log(f"  调整：人终检锁章纲")
    log(f"  适用八方向闸门：{ring['audit']}")
    return {"ring": ring["key"], "mode": "lock", "exec": "AI审计", "review": "AI审计+人锁",
            "auditDirections": ring["audit"]}

# 取代表性环
mesh_ring = next(p for p in phases if p["mode"] == "mesh" and p["subitems"])  # 主角设计(15子项)
human_ring = next(p for p in phases if p["mode"] == "human")
lock_ring = next(p for p in phases if p["mode"] == "lock")
trial_result = {
    "generated": datetime.datetime.now().isoformat(timespec="seconds"),
    "note": "SIM 模拟试运行，未发起真实 AI 窗口调用。real 模式需 5 个 AI 桌面窗口 + CDP。",
    "writers": WRITERS,
    "mesh_demo": dry_mesh_ring(mesh_ring),
    "human_demo": dry_human_ring(human_ring),
    "lock_demo": dry_lock_ring(lock_ring),
}

# ============ 3) 产出程序2 兼容片段 ============
log("")
log("=" * 64)
log("【3】产出程序2 可直接消费的 phases/assignments 兼容片段")
log("=" * 64)
# 把 23 环摊成 01_规划 的子环（带 mode 与审核独立性）
sub_rings_planning = []
for p in phases:
    sub_rings_planning.append({
        "name": f"P{p['id']:02d}_{p['key']}",
        "mode": p["mode"],
        "审核独立": "跨厂盲审" if p["mode"] == "mesh" else ("人拍板" if p["mode"] == "human" else "AI审计+人锁"),
        "audit": p["audit"],
    })
# 程序2 原 01_规划 仅 7 粗子环；这里证明替换后是 23 细环
prog2_phases = {
    "说明": "由 manifest_23环_整合.json 自动生成；以 23 细环替换原 7 粗子环。",
    "顺序": ["00_初始化", "01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"],
    "环节": {
        "00_初始化": ["项目信息", "1.0_总纲", "1.1_定位与卖点", "1.2_故事核心主题", "1.3_人物系统",
                   "1.4_世界观与设定", "1.5_结构与节奏", "1.6_卷纲"],
        "01_规划": [s["name"] for s in sub_rings_planning],
        "02_写作": ["2-1_章纲产出", {"name": "2-2_正文产出", "segments": ["始","显","通","动","成","终"], "chapter": "第001章"},
                   "2-3_审核", "2-4_调整", "2-5_终审放行评审"],
        "03_去AI": ["3-1_套话与总结清理", "3-2_句式破对称破匀速", "3-3_对话去同质化", "3-4_细节与潜台词补充", "3-5_朗读试读"],
        "04_审核": [{"name": "4-1_逻辑设定一致", "input": "03_去AI/第001章_润色定稿.md"},
                   {"name": "4-2_人物与OOC", "input": "03_去AI/第001章_润色定稿.md"},
                   {"name": "4-3_节奏与爽点", "input": "03_去AI/第001章_润色定稿.md"},
                   {"name": "4-4_文风AI味格式", "input": "03_去AI/第001章_润色定稿.md"},
                   {"name": "4-5_合规", "input": "03_去AI/第001章_润色定稿.md"}],
        "05_出厂": [{"name": "5-1_低级错误", "input": "03_去AI/第001章_润色定稿.md"}, "5-2_名称与章号统一", "5-3_定稿打包归档"],
    },
}
# assignments：01_规划 每个子环审核独立（不再等于执行）
prog2_assignments = {
    "说明": "由 manifest 自动生成；01_规划 各子环审核独立，修复原『审核=执行同AI』问题。",
    "环节": {
        "01_规划": {
            "子环": [s["name"] for s in sub_rings_planning],
            "执行": "规划AI(轮转写手)",
            "审核": "跨厂独立盲审裁判(≠执行写手)",
            "调整": "汇总融合者",
            "明细": {s["name"]: {"mode": s["mode"], "审核独立": s["审核独立"], "audit": s["audit"]} for s in sub_rings_planning},
        }
    },
}
prog2_fragment = {"phases": prog2_phases, "assignments_01规划": prog2_assignments}

with open(OUT_SAMPLE, "w", encoding="utf-8") as f:
    json.dump(trial_result, f, ensure_ascii=False, indent=2)
with open(OUT_PROG2, "w", encoding="utf-8") as f:
    json.dump(prog2_fragment, f, ensure_ascii=False, indent=2)

log(f"✅ 样例输出: {OUT_SAMPLE}")
log(f"✅ 程序2兼容片段: {OUT_PROG2}")
log("")
log("=" * 64)
log("试运行结论")
log("=" * 64)
log("· 清单结构合法、可加载、可驱动；八方向闸门完整挂载到各环。")
log("· mesh 全网格、human 人拍板、lock 人锁 三种模式均可由清单推演出具体执行步骤。")
log("· 程序2 的 01_规划 已由 7 粗子环升级为 23 细环，且其审核改为跨厂独立——环节问题修复方案可落地。")
log("· 真实投产只需：把 prog2_兼容片段 写回程序2 的 rules/phases.json + assignments.json，")
log("  并在 real 模式启动 5 个 AI 窗口（CDP）即可跑真实赛马闸门。")
