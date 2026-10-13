# -*- coding: utf-8 -*-
"""build_project_config.py — 生成「按项目」的 37 环配置（phases.json / assignments.json / prompts/）。

解决三件事：
  1) 子项拆分：规划环节可携带 items（子项码 + 名称 + 要求），引擎逐子项独立出文件。
  2) 模板 desc 源：提示词由 apps.json / blocks.json 的真实 desc 注入（修复旧版「无额外说明」）。
  3) 每环独立指派 AI：assignments.json 按环记录 mode / writers / judges / merger / 审核 / 调整。

用法（命令行）：
  python build_project_config.py --template 疯骨56 --out <config目录>
  python build_project_config.py --template 通用37环 --out <config目录>
  python build_project_config.py --blocks <自定义blocks.json> --out <config目录>

被 collab_app 调用：build_config(template, out_dir, blocks_path=None)
"""

import os
import sys
import json
import shutil

# 路径（脚本位于 app/ 下，直接用绝对 path 取设计源，避免依赖 cwd）
_THIS = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(_THIS)
_APPS = os.path.join(APP_ROOT, "windows-use", "_scratch", "apps.json")
_BLOCKS_DEFAULT = r"C:\Users\Administrator\Desktop\AI输出\_scripts\blocks.json"
_RULES = os.path.join(APP_ROOT, "rules")
# 全局提示词目录（人工打磨过的模板，项目级模板优先继承这里，避免空洞内容覆盖）
_GLOBAL_PROMPTS = os.path.join(APP_ROOT, "prompts")

DEFAULT_WRITERS = ["豆包", "通义千问", "DeepSeek", "Kimi", "腾讯元宝"]
DEFAULT_JUDGES = ["智谱清言", "文心一言", "讯飞星火"]   # 跨厂裁判，避免同源偏置
DEFAULT_MERGER = "豆包"


# ---------------------------------------------------------------- 设计源读取
def load_apps():
    with open(_APPS, encoding="utf-8") as f:
        return json.load(f)


def load_blocks(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_current_phases():
    with open(os.path.join(_RULES, "phases.json"), encoding="utf-8") as f:
        return json.load(f)


def load_current_assignments():
    p = os.path.join(_RULES, "assignments.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


# ---------------------------------------------------------------- 规划环节构造
def _规划_rings_generic(apps):
    """通用 37 环：取 apps.json 中 stage==规划 的全部 phase，每个环 = 1 个整体任务。"""
    rings = []
    for p in apps.get("phases", []):
        if p.get("stage") == "规划":
            rings.append({
                "name": p.get("key"),
                "mode": p.get("mode") or "mesh",
                "desc": (p.get("desc") or "").strip(),
            })
    return rings


def _规划_rings_from_blocks(blocks):
    """疯骨56 / 导入：每个 blocks 组 = 一个规划环，组内的 blocks = 子项（items）。"""
    rings = []
    for grp, gv in blocks.items():
        phase = gv.get("phase") or grp
        blk = gv.get("blocks") or {}
        items = []
        for code, bv in blk.items():
            if isinstance(bv, dict):
                items.append({
                    "code": code,
                    "name": bv.get("name") or code,
                    "desc": (bv.get("desc") or "").strip(),
                })
            else:
                items.append({"code": code, "name": str(bv), "desc": ""})
        rings.append({
            "name": phase,
            "mode": "mesh",
            "items": items,
        })
    return rings


# ---------------------------------------------------------------- 指派构造
def _assign_for_ring(ring):
    """为单个环生成默认指派（mode / writers / judges / merger / 审核 / 调整）。"""
    mode = ring.get("mode") or "mesh"
    writers = list(DEFAULT_WRITERS)
    judges = list(DEFAULT_JUDGES)
    merger = DEFAULT_MERGER
    # 审核/调整：用裁判池首名 / 汇总者兜底
    return {
        "mode": mode,
        "writers": writers,
        "judges": judges,
        "merger": merger,
        "审核": judges[0] if judges else merger,
        "调整": merger,
    }


def _build_assignments(phases, cur_assign):
    """构造 assignments.json：00 沿用，01 由 rings 生成，02-05 尽量沿用已有明细。"""
    out = {"说明": "每环独立指派 AI；明细键 = 环节内的环名。", "环节": {}}
    # 00_初始化
    out["环节"]["00_初始化"] = cur_assign.get("环节", {}).get("00_初始化", {
        "子环": ["项目信息", "1.0_总纲"], "执行": "", "审核": "", "调整": ""})
    # 01_规划
    rings = phases["环节"]["01_规划"]
    detail = {}
    for r in rings:
        nm = r.get("name")
        detail[nm] = _assign_for_ring(r)
    out["环节"]["01_规划"] = {
        "子环": [r.get("name") for r in rings],
        "明细": detail,
        "执行": "", "审核": DEFAULT_JUDGES[0], "调整": DEFAULT_MERGER,
    }
    # 02-05 沿用已有
    for st in ("02_写作", "03_去AI", "04_审核", "05_出厂"):
        out["环节"][st] = cur_assign.get("环节", {}).get(st, {
            "子环": [], "明细": {}, "执行": "", "审核": DEFAULT_JUDGES[0], "调整": DEFAULT_MERGER})
    return out


# ---------------------------------------------------------------- 提示词生成
# 注意：占位符必须最终写成 {{输入}} / {{平台规则}} / {{产物目录}}（双花括号），
# 因为 phase_runner 替换的是这三个双花括号标记。这里因为要走 .format()，
# 所以源码里写四花括号，转义后落到文件里才是双花括号。
_PROMPT_HEAD = (
    "# {ring}（{stage}）\n\n"
    "## 一、任务要求\n{desc}\n\n"
    "## 二、本环节赛马机制\n{mech}\n\n"
    "## 三、输入资料\n{{{{输入}}}}\n\n"
    "## 四、平台规则（如适用）\n{{{{平台规则}}}}\n\n"
    "## 五、产物目录\n{{{{产物目录}}}}\n\n"
    "## 六、产出要求\n请按上述任务要求产出完整内容，写到本子项目录的 final.md（赛马环由汇总者融合）。\n"
)

# 复合环六要素的分工说明（写正文/分布分段时附在段模板末尾，避免各段产出同质）
_SEG_HINT = {
    "始": "开场段：交代场景、人物状态与钩子，必须在前 200 字内抓住读者；只做引入，不展开冲突。",
    "显": "显段：把主角的核心欲望/困境摆到台面，让读者明确本段要解决什么。",
    "通": "通段：交代必要背景与阻力来源，铺垫信息，不重复前文已交代的内容。",
    "动": "动段：冲突真正爆发，推进力最强的一段；动作/对抗/博弈写实，写出压迫与反扑。",
    "成": "成段：矛盾得到阶段性解决或局势反转，给出阶段性爽点，但不要一次收尾。",
    "终": "终段：收束本段情绪与节奏，抛出下一段的钩子（悬念/危机/反转），不要平收。",
}

# phases.json 里 desc 为空、且全局 prompts 没有手写模板的环，给一份像样的职责说明，
# 避免生成"（见上游资料…）"这种等于没写的提示词
_RING_DESC_FALLBACK = {
    "项目信息": "汇总并固化本项目的基础设定：题材、频道、主角、章节数、核心金手指，"
                "输出结构化的《项目信息卡》，供后续所有环节引用。",
    "1.0_总纲": "写全书的总纲：一句故事、核心卖点、主题立意、主角成长主线与全书终局，"
                "作为后续规划与写作的最高依据。",
    "1.1_定位与卖点": "明确作品定位（赛道/频道/对标）、目标读者画像与核心卖点，"
                      "输出可直接用于书名简介与推荐的定位说明。",
    "1.2_故事核心主题": "写清故事核心矛盾与主题表达：主角要什么、被什么阻挡、"
                        "主题如何通过剧情体现。",
    "1.3_人物系统": "搭建人物系统：主角、核心配角、反派的功能定位、关系图与成长弧，"
                    "确保每个人物都有可写的行为动机。",
    "1.4_世界观与设定": "写最小可行的世界观设定集：力量体系/规则、地理与势力、"
                        "关键规则及其限制，避免设定冲突。",
    "1.5_结构与节奏": "规划全书结构与节奏：分卷、每卷功能、爽点分布与情绪曲线。",
    "1.6_卷纲": "把结构拆成卷级纲要：每卷的目标、冲突、关键转折与收束。",
}


def _mech_text(mode):
    if mode == "mesh":
        return ("多人赛马：{n} 名写手各自独立撰写 → 匿名交叉盲审（互看不到作者）→ "
                "汇总者择优融合为一份最终稿。").format(n=len(DEFAULT_WRITERS))
    if mode == "human":
        return "AI 出候选稿，由人工拍板定稿（pending.json → final.md）。"
    if mode == "lock":
        return "AI 审计 + 人工锁定放行（audit.md → locked.json → final.md）。"
    return "单人串行：执行者产出 → 审核者评审 →（如需）调整者修改。"


def gen_prompt(ring, desc, mode, stage):
    desc = desc or _RING_DESC_FALLBACK.get(ring) or "（见上游资料与全局规划，按本环节目标产出）"
    mech = _mech_text(mode)
    return _PROMPT_HEAD.format(ring=ring, desc=desc, mech=mech, stage=stage)


def _write_prompts(prompts_dir, phases):
    """写项目级提示词。

    原则：**优先继承全局 prompts/ 里已写好的模板**（那是人工打磨过的真内容，
    含各环节标准、六要素、质检条目），只有全局没有对应模板时才生成兜底。
    绝不用空洞的自动生成内容去覆盖手写模板——引擎读项目级 config/prompts，
    覆盖等于把好模板废掉。
    """
    os.makedirs(prompts_dir, exist_ok=True)
    # _通用.md 兜底（根）
    generic = (
        "# 通用子项任务\n\n"
        "## 任务要求\n请基于输入资料完成本子项产出。\n\n"
        "## 输入资料\n{{输入}}\n\n## 平台规则\n{{平台规则}}\n\n"
        "## 产物目录\n{{产物目录}}\n"
    )
    with open(os.path.join(prompts_dir, "_通用.md"), "w", encoding="utf-8") as f:
        f.write(generic)

    n_copy = n_gen = 0
    for st, rings in phases["环节"].items():
        sd = os.path.join(prompts_dir, st)
        os.makedirs(sd, exist_ok=True)
        # 每环节一份 _通用.md 兜底（引擎缺专属模板时按环节回退）
        gpath = os.path.join(_GLOBAL_PROMPTS, st, "_通用.md")
        if os.path.exists(gpath):
            shutil.copyfile(gpath, os.path.join(sd, "_通用.md"))
        else:
            with open(os.path.join(sd, "_通用.md"), "w", encoding="utf-8") as f:
                f.write("# %s · 通用任务模板\n\n" % st)
                f.write("请基于输入资料完成本环节本环的任务。\n\n"
                        "## 输入资料\n{{输入}}\n\n## 平台规则\n{{平台规则}}\n\n"
                        "## 产物目录\n{{产物目录}}\n")

        for r in rings:
            if isinstance(r, str):
                nm, mode, segs = r, "mesh", []
            elif isinstance(r, dict):
                nm = r.get("name")
                mode = r.get("mode") or "mesh"
                segs = r.get("segments") or []
            else:
                continue
            if not nm:
                continue
            dst = os.path.join(sd, nm + ".md")
            src = os.path.join(_GLOBAL_PROMPTS, st, nm + ".md")
            if os.path.exists(src):
                shutil.copyfile(src, dst)      # 继承手写模板
                n_copy += 1
            else:
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(gen_prompt(nm, (r.get("desc") if isinstance(r, dict) else "") or "",
                                       mode, st))
                n_gen += 1
            # 子项（规划环节细分）：逐子项独立模板
            for it in ((r.get("items") or []) if isinstance(r, dict) else []):
                code = it.get("code") or it.get("name")
                d2 = os.path.join(sd, "%s__%s.md" % (nm, code))
                s2 = os.path.join(_GLOBAL_PROMPTS, st, "%s__%s.md" % (nm, code))
                if os.path.exists(s2):
                    shutil.copyfile(s2, d2)
                else:
                    with open(d2, "w", encoding="utf-8") as f:
                        f.write(gen_prompt("%s · %s" % (nm, it.get("name")),
                                           it.get("desc", ""), mode, st))
            # 复合环分段：继承环模板 + 追加本段职责（否则各段产出同质化）
            for seg in segs:
                d3 = os.path.join(sd, "%s__%s.md" % (nm, seg))
                with open(d3, "w", encoding="utf-8") as f:
                    f.write(_seg_prompt(nm, seg, st, mode))
                n_gen += 1
    return n_copy, n_gen


def _seg_prompt(ring, seg, stage, mode):
    """复合环的分段模板 = 环模板全文 + 本段职责说明。"""
    base = ""
    src = os.path.join(_GLOBAL_PROMPTS, stage, ring + ".md")
    if os.path.exists(src):
        base = open(src, encoding="utf-8").read().rstrip() + "\n\n"
    if not base:
        base = gen_prompt(ring, "", mode, stage).rstrip() + "\n\n"
    head = "# %s · %s段（%s）\n\n" % (ring, seg, stage)
    tail = ("---\n\n## 本段专属职责（%s段）\n%s\n\n"
            "**只写本段**，不要越界写其它段的内容；与前一段自然衔接。\n"
            % (seg, _SEG_HINT.get(seg, "按六要素中「%s」的定位完成本段。" % seg)))
    # 去掉继承来的旧标题，拼上新标题
    if base.startswith("# "):
        nl = base.find("\n")
        base = base[nl + 1:] if nl > 0 else ""
    return head + base + tail


# ---------------------------------------------------------------- 总装
def build_config(template="疯骨56", out_dir=None, blocks_path=None):
    """生成一份按项目配置到 out_dir（含 phases.json / assignments.json / prompts/）。

    template: "疯骨56" | "通用37环" | "导入"(需 blocks_path)
    """
    if not out_dir:
        raise ValueError("out_dir 必填")
    apps = load_apps()
    cur_assign = load_current_assignments()
    cur_phases = load_current_phases()

    if template == "疯骨56":
        blocks = load_blocks(blocks_path or _BLOCKS_DEFAULT)
        rings01 = _规划_rings_from_blocks(blocks)
        tpl_label = "疯骨56子项"
    elif template == "通用37环":
        rings01 = _规划_rings_generic(apps)
        tpl_label = "通用37环"
    elif template == "导入":
        if not blocks_path or not os.path.exists(blocks_path):
            raise ValueError("导入模式需要有效的 blocks_path")
        blocks = load_blocks(blocks_path)
        rings01 = _规划_rings_from_blocks(blocks)
        tpl_label = "导入blocks"
    else:
        raise ValueError("未知 template: %s" % template)

    phases = {
        "说明": "37 环设计（程序二改装 · 32流程版）；01_规划 可含 items 子项拆分。",
        "顺序": ["00_初始化", "01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"],
        "环节": {
            "00_初始化": cur_phases["环节"].get("00_初始化", ["项目信息", "1.0_总纲"]),
            "01_规划": rings01,
            "02_写作": cur_phases["环节"].get("02_写作", []),
            "03_去AI": cur_phases["环节"].get("03_去AI", []),
            "04_审核": cur_phases["环节"].get("04_审核", []),
            "05_出厂": cur_phases["环节"].get("05_出厂", []),
        },
        "说明_集成": "模板来源：%s" % tpl_label,
    }

    assignments = _build_assignments(phases, cur_assign)

    # 写出
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "phases.json"), "w", encoding="utf-8") as f:
        json.dump(phases, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "assignments.json"), "w", encoding="utf-8") as f:
        json.dump(assignments, f, ensure_ascii=False, indent=2)
    _write_prompts(os.path.join(out_dir, "prompts"), phases)

    # 统计
    n_items = sum(len(r.get("items", [])) for r in rings01 if isinstance(r, dict))
    return {
        "out_dir": out_dir,
        "template": tpl_label,
        "规划环数": len(rings01),
        "规划子项数": n_items,
        "prompts数": sum(len(r.get("items", [1])) if isinstance(r, dict) else 1
                         for r in rings01),
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="疯骨56", choices=["疯骨56", "通用37环", "导入"])
    ap.add_argument("--out", required=True, help="目标 config 目录")
    ap.add_argument("--blocks", default=None, help="导入模式：blocks.json 路径")
    args = ap.parse_args()
    if args.template == "导入" and not args.blocks:
        ap.error("导入模式需 --blocks")
    res = build_config(args.template, args.out, args.blocks)
    print(json.dumps(res, ensure_ascii=False, indent=2))
