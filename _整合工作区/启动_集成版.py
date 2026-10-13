# -*- coding: utf-8 -*-
"""
启动_集成版（Integrated Launcher）
===============================
动作（全部只在 F:\赛马23环整合工作室 内，原盘不动）：
  STEP 1  写回：把《23 环·八方向》集成配置写回 备份副本 的 rules
                - phases.json 的 01_规划 由粗 7 环 → 细 23 环
                - assignments.json 的 01_规划 由「审核=执行同AI」→ 跨厂独立盲审
                写回前先对原 rules 生成 .bak_integrated 安全备份
  STEP 2  启动：加载写回后的集成配置 + manifest，校验合法性，
                用 SIM 模式端到端跑通全部 23 环（不调真实 AI 窗口）：
                  mesh  → N写 → N-1盲审 → 汇总择优 → 冠军
                  human → AI候选 + 人拍板
                  lock  → 八方向逐方向审计 + 人锁
                产出 启动日志 + 每环冠军 + 集成配置快照

说明：SIM 启动验证「集成配置可加载、可驱动、可贯穿 23 环」。
      真实投产 = 把本配置写回你原盘程序2 的 rules + 打开 5 个 AI 窗口(CDP) + real 模式。
"""
import json, os, datetime, hashlib, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)                                   # F:\赛马23环整合工作室
RULES = os.path.join(ROOT, "_backup_程序2协同写作", "rules")
MANIFEST = os.path.join(BASE, "manifest_23环_整合.json")
FRAG = os.path.join(BASE, "prog2_兼容片段_试运行.json")
PHASES = os.path.join(RULES, "phases.json")
ASSIGN = os.path.join(RULES, "assignments.json")
RUN_LOG = os.path.join(BASE, "启动_运行日志.json")
RUN_TXT = os.path.join(BASE, "启动_运行日志.txt")

WRITERS = ["豆包", "千问", "ZCode", "WorkBuddy", "Qoder"]      # 示例阵容（与 mix_send 一致）

def log(s, out):
    out.append(s)
    print(s)

# ============================ STEP 1：写回 ============================
def step1_writeback():
    out = []
    log("=" * 70, out)
    log("STEP 1  写回 23 环集成配置 → F盘备份副本 rules（原盘不动）", out)
    log("=" * 70, out)

    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    frag = json.load(open(FRAG, encoding="utf-8"))
    phases_orig = json.load(open(PHASES, encoding="utf-8"))
    assign_orig = json.load(open(ASSIGN, encoding="utf-8"))

    # 安全备份原 rules（覆盖式幂等：只备一次）
    for fn in ("phases.json", "assignments.json"):
        src = os.path.join(RULES, fn)
        bak = os.path.join(RULES, fn + ".bak_integrated")
        if not os.path.exists(bak):
            shutil.copy2(src, bak)
            log(f"  🔒 已安全备份原 {fn} → {fn}.bak_integrated", out)

    # —— 1a) phases.json：01_规划 替换为 23 细环 ——
    frag_phases = frag["phases"]
    new_plan = frag_phases["环节"]["01_规划"]            # P01..P23 名称列表
    phases_orig["环节"]["01_规划"] = new_plan
    phases_orig["说明_集成"] = "已由 启动_集成版.py 写回：01_规划 7粗环→23细环（赛马机制·规划23环）。"
    json.dump(phases_orig, open(PHASES, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    log(f"  ✅ phases.json·01_规划：{len(new_plan)} 细环已写回（原 {7} 粗环）", out)

    # —— 1b) assignments.json：01_规划 替换为跨厂独立版 ——
    frag_assign_block = frag["assignments_01规划"]["环节"]["01_规划"]
    assign_orig["环节"]["01_规划"] = frag_assign_block
    json.dump(assign_orig, open(ASSIGN, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    # 统计 mode 分布
    modes = {}
    for k, v in frag_assign_block["明细"].items():
        modes[v["mode"]] = modes.get(v["mode"], 0) + 1
    log(f"  ✅ assignments.json·01_规划：审核改为跨厂独立，mode 分布 = {modes}", out)
    log("  （已修复原『1-1_定位与卖点 执行=审核=调整=WorkBuddy』同AI自审问题）", out)
    return out

# ============================ STEP 2：启动 ============================
def sim_mesh(ring, out):
    key = ring["key"]; rid = ring["id"]; sub = ring["subitems"]
    log(f"\n  ● MESH [{rid:02d}] {key}  子项={sub or '—'}", out)
    log(f"    执行：{len(WRITERS)} 写手各写 1 份 chunk（全网格赛马）", out)
    # 确定性伪盲审（仅示意，非真实评分）
    scores = {}
    for reviewer in WRITERS:
        scores[reviewer] = {}
        for writer in WRITERS:
            if writer == reviewer: continue
            h = int(hashlib.md5(f"{key}|{reviewer}|{writer}".encode()).hexdigest(), 16) % 4 + 7
            scores[reviewer][writer] = h
    avg = {}
    for writer in WRITERS:
        vals = [scores[r][writer] for r in WRITERS if r != writer]
        avg[writer] = round(sum(vals)/len(vals), 2)
    champ = max(avg, key=avg.get)
    log(f"    盲审：{len(WRITERS)}×{len(WRITERS)-1} 交叉矩阵 → 各写手均分 = {avg}", out)
    log(f"    🏆 冠军 = {champ}（{avg[champ]}）→ 个人最优版", out)
    if ring["audit"]:
        log(f"    八方向闸门：{ring['audit']}", out)
    return {"ring": key, "mode": "mesh", "champion": champ, "averages": avg, "audit": ring["audit"]}

def sim_human(ring, out):
    key = ring["key"]; rid = ring["id"]
    log(f"\n  ● HUMAN [{rid:02d}] {key}", out)
    log(f"    执行：AI 出候选/模板", out)
    log(f"    审核：人拍板  ← 修复点：不由 AI 自审", out)
    if ring["audit"]:
        log(f"    八方向闸门：{ring['audit']}", out)
    return {"ring": key, "mode": "human", "review": "人拍板", "audit": ring["audit"]}

def sim_lock(ring, out):
    key = ring["key"]; rid = ring["id"]
    log(f"\n  ● LOCK [{rid:02d}] {key}", out)
    log(f"    执行：AI 跑八方向逐方向审计 + 一致性/依赖", out)
    log(f"    审核：AI 审计 + 人终检锁章纲", out)
    log(f"    适用八方向：{ring['audit']}", out)
    return {"ring": key, "mode": "lock", "review": "AI审计+人锁", "audit": ring["audit"]}

def step2_launch():
    out = []
    log("", out)
    log("=" * 70, out)
    log("STEP 2  启动集成版：加载配置 + 校验 + SIM 跑通 23 环", out)
    log("=" * 70, out)

    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    phases_cfg = json.load(open(PHASES, encoding="utf-8"))
    assign_cfg = json.load(open(ASSIGN, encoding="utf-8"))
    phases = manifest["phases"]
    audit = manifest["auditDirections"]

    # —— 校验 ——
    errs = []
    if len(phases) != 23: errs.append(f"规划环数应为23，实为{len(phases)}")
    for p in phases:
        if p["mode"] not in {"mesh","human","lock"}: errs.append(f"环{p['key']} 模式非法")
    ring_names = {p["key"] for p in phases}
    for ad in audit:
        for r in ad["rings"] + ad["extends"]:
            if r not in ring_names: errs.append(f"八方向[{ad['key']}] 引用不存在环 {r}")
    # 校验写回是否生效：rules·phases 01_规划 应为 23
    if len(phases_cfg["环节"]["01_规划"]) != 23:
        errs.append(f"rules·phases 01_规划 写回未生效（{len(phases_cfg['环节']['01_规划'])}）")
    if errs:
        log("❌ 校验失败：", out)
        for e in errs: log("   - "+e, out)
        raise SystemExit("\n启动中止：配置校验未通过。")
    log("✅ 配置校验通过：23环 / 8方向 / 模式合法 / 写回生效", out)

    # —— 端到端跑 23 环 ——
    log("", out)
    log(f"【启动】SIM 模式跑通 23 环（阵容={WRITERS}）", out)
    results = []
    for p in phases:
        if p["mode"] == "mesh":
            results.append(sim_mesh(p, out))
        elif p["mode"] == "human":
            results.append(sim_human(p, out))
        else:
            results.append(sim_lock(p, out))

    # —— 汇总 ——
    champions = [(r["ring"], r["champion"]) for r in results if r["mode"] == "mesh"]
    log("", out)
    log("=" * 70, out)
    log("启动结果汇总", out)
    log("=" * 70, out)
    log(f"· 23 环全部跑通：mesh={sum(1 for r in results if r['mode']=='mesh')} "
        f"human={sum(1 for r in results if r['mode']=='human')} "
        f"lock={sum(1 for r in results if r['mode']=='lock')}", out)
    log(f"· mesh 冠军分布：", out)
    from collections import Counter
    c = Counter(champ for _, champ in champions)
    for w, n in c.most_common():
        log(f"    {w}: {n} 冠", out)
    log("· 集成版已可启动驱动；真实投产见脚本顶部说明。", out)
    return out, results

if __name__ == "__main__":
    out1 = step1_writeback()
    out2, results = step2_launch()
    full = out1 + out2
    # 落盘日志
    json.dump({"generated": datetime.datetime.now().isoformat(timespec="seconds"),
               "mode": "SIM（未调真实 AI 窗口）",
               "log": full,
               "results": results},
              open(RUN_LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    with open(RUN_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(full))
    print("\n✅ 启动完成。日志：")
    print("   ", RUN_LOG)
    print("   ", RUN_TXT)
