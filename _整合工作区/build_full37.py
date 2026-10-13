# -*- coding: utf-8 -*-
r"""
把第一版设计源 apps.json 里【尚未接入的 14 个环节】全部接入 32流程版。

设计源共 37 环 = 规划23(已接入) + 写作4 + 润色1 + 质检9
本脚本接入后 14 环：
    写作4 -> 02_写作   (W1..W4)
    润色1 -> 03_去AI   (R1)
    质检9 -> 04_审核   (Q1..Q9)

改动只发生在 F:\赛马23环整合工作室\程序2改装版\rules\ （F盘副本内），原盘不动。
写回前自动生成 .bak_full37 备份。
"""
import json, shutil, os

SRC = r"F:\赛马23环整合工作室\_backup_第一版23环设计\协同层\配置\apps.json"
RULES = r"F:\赛马23环整合工作室\程序2改装版\rules"
PH = os.path.join(RULES, "phases.json")
AS = os.path.join(RULES, "assignments.json")

d = json.load(open(SRC, encoding="utf-8"))
ph = d["phases"]
ad = d.get("auditDirections", [])

INDEP = {"mesh": "跨厂盲审", "human": "人拍板", "lock": "AI审计+人锁", "storage": "归档入库"}
SIX = ["始", "显", "通", "动", "成", "终"]
POLISH_SECTIONS = [
    "一、润色前准备(1-5)",
    "二、常规润色(6-11)",
    "三、去AI味专项(12-25)",
    "四、朗读试读(26-28)",
    "五、润色终审(出口)",
]


def build_audit(p, stage):
    """该环适用的审核/质量标准来源。

    重要：八方向 auditDirections 只覆盖【规划环】，
    写作 / 润色 / 质检 各有自身标准，故此处按 stage 挂载对应标准。
    """
    out = []
    # 先看是否命中八方向（主要是规划环，写作/质检通常为空）
    for a in ad:
        rings = a.get("rings")
        if isinstance(rings, (list, str)) and p["key"] in rings:
            out.append(a.get("key"))

    if stage == "写作":
        if p.get("six"):
            out.append("六要素(始·显·通·动·成·终)")
        if p.get("supp"):
            out.append("支撑上下文注入")
    elif stage == "润色":
        out.append("polishStandard 四节28子项")
    elif stage == "质检":
        secs = p.get("qcSecs")
        if secs:
            out.append("qcStandard 节" + "/".join(secs))

    if p.get("craft"):
        out.append("craft：" + str(p.get("craft")))
    if p.get("mode") == "lock":
        out.append("人锁终审")
    return out


# ---------------- 备份 ----------------
for f in (PH, AS):
    bak = f + ".bak_full37"
    if not os.path.exists(bak):
        shutil.copy2(f, bak)
        print("备份 ->", os.path.basename(bak))
    else:
        print("备份已存在 ->", os.path.basename(bak))

phases = json.load(open(PH, encoding="utf-8"))
assign = json.load(open(AS, encoding="utf-8"))

# ---------------- 取未接入的 14 环 ----------------
rest = ph[23:37]
by_stage = {}
for p in rest:
    by_stage.setdefault(p.get("stage"), []).append(p)

PREFIX = {"写作": "W", "润色": "R", "质检": "Q"}
STAGE2FILE = {"写作": "02_写作", "润色": "03_去AI", "质检": "04_审核"}

report = []
total = 0

for stage in ["写作", "润色", "质检"]:
    file_stage = STAGE2FILE[stage]
    items, detail = [], {}
    for i, p in enumerate(by_stage.get(stage, []), 1):
        key = p["key"]
        mode = p.get("mode")
        nid = f"{PREFIX[stage]}{i}_{key}"

        entry = {"name": nid}
        if p.get("six"):
            entry["segments"] = SIX
            entry["six"] = True
        if p.get("polish"):
            entry["sections"] = POLISH_SECTIONS
        if p.get("qcSecs"):
            entry["qcSecs"] = p["qcSecs"]
        if p.get("craft"):
            entry["craft"] = p["craft"]
        entry["mode"] = mode
        items.append(entry)

        au = build_audit(p, stage)
        detail[nid] = {"mode": mode, "审核独立": INDEP.get(mode, "待定"), "audit": au}
        report.append((file_stage, nid, mode, INDEP.get(mode, "待定"), au))
        total += 1

    phases["环节"][file_stage] = items
    # assignments：保留该阶段原有默认角色，追加明细
    node = assign["环节"][file_stage]
    node["子环"] = [it["name"] for it in items]
    node["明细"] = detail

# ---------------- 说明 ----------------
phases["说明_集成"] = (
    "已接入第一版设计源 apps.json 全部 37 环："
    "01_规划=规划23环(P01-P23)；02_写作=写作4环(W1-W4)；"
    "03_去AI=润色1环(R1，含润色四节+终审)；04_审核=质检9环(Q1-Q9)。"
    "00_初始化 与 05_出厂 为程序2 自有收尾阶段，设计源无对应，予以保留；"
    "其中 05_出厂/5-1_低级错误 与 Q7_上架前低级错误检查 存在职责重叠，已在说明中标注。"
)

json.dump(phases, open(PH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(assign, open(AS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------------- 报告 ----------------
print("\n=== 本次接入 %d 环 ===" % total)
cur = ""
for fs, nid, mode, indep, au in report:
    if fs != cur:
        print(f"\n[{fs}]")
        cur = fs
    src = "、".join(au) if au else "(无)"
    print(f"   {nid:<26} mode={mode:<8} 审核={indep:<10} 标准={src}")

print("\n=== 写回后各阶段环数 ===")
tot = 0
for stage, items in phases["环节"].items():
    n = len(items)
    tot += n
    mark = ""
    if stage in ("02_写作", "03_去AI", "04_审核"):
        mark = "  <-- 本次接入"
    elif stage == "01_规划":
        mark = "  <-- 此前接入"
    print(f"   {stage}: {n} 环{mark}")
print(f"   合计 = {tot} 环")
print("\n设计源 37 环落地情况: 规划23 + 写作4 + 润色1 + 质检9 = 37 -> 全部接入")
