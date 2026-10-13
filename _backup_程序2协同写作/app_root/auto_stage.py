"""auto_stage.py — 程序二·协同写作「自动执行引擎」（真实接入 mix_send）。

职责（读块上下文 → 拼提示 → 调对应 AI → 写回）：
  1. 产出：每块按指派 AI 发送任务（注入上游累积稿 + 可选指令文件 cmds/），AI 写盘后读取。
  2. 审核：送「审核者 AI」用 stage_board.build_review_prompt（按 norms 门控自动屏蔽规范子标准）。
  3. 修改：送「调整者 AI」按审核意见改稿。
  4. （终审子步）只出终审意见，不调整。

发送层：dry-run 落占位产物（可反复验证整条链路）；real 走 windows-use/mix_send.send
直接把任务投给对应 AI 窗口，并轮询 AI 写盘文件作为回执。

门控：
  · 评估门控来自 stage_board.active_sub_keys（正文前 norms=False → 屏蔽规范评估）。
  · 大环节手动放行由 UI/run_state 控制；run_all() 为「全自动」才会自动放行。

本文件不修改 core/、mix_send.py、ai_apps.json —— 纯新增（真实执行逻辑承载于此）。
collab_exec.py 作为对外兼容薄封装，仅 re-export 本模块符号。
"""
import os
import sys
import time
import glob
import json
import threading
import re
import glob
import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导

sys.path.insert(0, paths.WINDOWS_USE)

from stage_board import (load, save, PIPELINE, STAGE_ORDER, build_review_prompt,
                         user_passes_gate, new_run_state,
                         set_item_status, cascade_fail_from_item,
                         stage_failed_steps, stage_all_passed)

# 真实发送：直接调用 windows-use/mix_send.send（CDP/pyautogui 投递到对应 AI 窗口）
from mix_send import send as _mix_send, capture_with_meta as _mix_capture
from players import load_players as _load_players

# 兼容性：GBK 控制台（cmd/部分 .bat）无法编码 emoji，统一把 stdout/stderr 设为 utf-8 容错，
# 避免在本模块或 GUI 进程里任何意外 print 时崩溃（GUI 日志本身走 QTextEdit，unicode 安全）。
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

COLLAB_ROOT = paths.join("work", "collab")
ART_ROOT = os.path.join(COLLAB_ROOT, "_artifacts")
CTX_ROOT = os.path.join(COLLAB_ROOT, "_context")
CMD_ROOT = os.path.join(COLLAB_ROOT, "cmds")

DRY_RUN = True
_STOP = False
_PAUSE = False
_PROJECT_WS = None

# ----------------------------------------------------------------- 连通性模拟开关
# MOCK_PROMPTS = True  → 运行时不发送真实提示词，只给每个 AI 投极简指令：
#   「请创建/写入文件《规定名》，内容只写：你好」，用于先验证 AI 连通性与文件落盘，避免反复消耗。
# 真实提示词已整体备份在 工作空间/_备份_真实提示词_*/ 下，不会丢失。
# 连通性验证通过后，把此处改为 False 并重启应用，即恢复真实提示词全流程。
MOCK_PROMPTS = False


def set_dry_run(v):
    global DRY_RUN
    DRY_RUN = bool(v)


def set_project_workspace(path):
    """设置当前项目工作区根目录；runner 会把产物写到该目录下的 01~05 子文件夹。"""
    global _PROJECT_WS
    _PROJECT_WS = path


def _project_ws():
    return _PROJECT_WS or COLLAB_ROOT


def start_run():
    global _STOP, _PAUSE
    _STOP = False
    _PAUSE = False


def stop():
    global _STOP
    _STOP = True


def pause():
    global _PAUSE
    _PAUSE = True


def resume():
    global _PAUSE
    _PAUSE = False


def _reset_stop():
    global _STOP, _PAUSE
    _STOP = False
    _PAUSE = False


# ----------------------------------------------------------------- 路径/IO
def _mkdir(p):
    os.makedirs(p, exist_ok=True)


def _write(path, text):
    _mkdir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _stage_dir(stage_key):
    idx = STAGE_ORDER.index(stage_key) + 1
    return os.path.join(_project_ws(), f"{idx:02d}_{stage_key}")


def _logs_dir():
    """全局操作/安排文件根（与产出目录同级）：<项目>/_logs/。"""
    return os.path.join(_project_ws(), "_logs")


def _logs_stage_dir(stage_key):
    """某环节的『操作/安排文件树』：<项目>/_logs/<NN>_<环节>/，
    本步骤规划、下一步建议、审核意见、调整稿、环节 context 索引都放这里，
    环节产出目录（<NN>_<环节>/）只留对写书有意义的成品文件。"""
    idx = STAGE_ORDER.index(stage_key) + 1
    return os.path.join(_logs_dir(), f"{idx:02d}_{stage_key}")


def _safe_name(name):
    """去掉 Windows 文件名非法字符（如 / 与 : * ? " < > |），用于环节或块名拼文件名。

    例如块名『句式破对称/破匀速』『文风/AI味/格式』含 /，直接拼会生成非法路径，
    这里统一去掉，使提示词查找与产物落盘路径一致（与现有提示词文件名对齐）。
    """
    return re.sub(r'[\/\\:*?"<>|]', '', name)


def _block_file(stage_key, step_name, block):
    st = next(s for s in PIPELINE if s["key"] == stage_key)
    step = next(s for s in st["steps"] if s["name"] == step_name)
    idx = step["blocks"].index(block) + 1
    return _safe_name(f"{STAGE_ORDER.index(stage_key)+1}-{idx}_{block}.md")


def _use_folder_layout(stage_key):
    """规划大环节保持原平铺结构；其余大环节按「子步名」分文件夹存放。"""
    return stage_key != "规划"


def _produce_path(stage_key, step_name, block, chapter=None):
    name = _block_file(stage_key, step_name, block)
    if chapter and chapter >= 1:
        name = f"第{chapter:03d}章_{_safe_name(block)}.md"
    if _use_folder_layout(stage_key):
        # 块产出按子步名单独建文件夹：正文→正文/ 、章纲→章纲/ …
        return os.path.join(_stage_dir(stage_key), step_name, name)
    return os.path.join(_stage_dir(stage_key), name)


def _review_path(stage_key, step_name, chapter=None, round=1):
    name = f"{step_name}_审核意见.md"
    if round and int(round) >= 2:
        name = f"{step_name}_审核意见_第{int(round)}轮.md"
    if chapter and chapter >= 1:
        name = f"第{chapter:03d}章_" + name
    # 审核意见属操作/安排类，统一放到 _logs/<环节>/<子步>审核意见/
    return os.path.join(_logs_stage_dir(stage_key), f"{step_name}审核意见", name)


def _adjust_path(stage_key, step_name, chapter=None, round=1):
    name = f"{step_name}_调整稿.md"
    if round and int(round) >= 2:
        name = f"{step_name}_调整稿_第{int(round)}轮.md"
    if chapter and chapter >= 1:
        name = f"第{chapter:03d}章_" + name
    # 调整稿属操作/安排类，统一放到 _logs/<环节>/<子步>调整稿/
    return os.path.join(_logs_stage_dir(stage_key), f"{step_name}调整稿", name)


def _context_path(stage_key):
    # 环节 context 是供下游读取的索引缓存（操作类），放到 _logs/<环节>/_context.md
    return os.path.join(_logs_stage_dir(stage_key), "_context.md")


def _build_context_index(stage_key, state):
    """生成本环节『产出索引』写入 _context.md：只列文件路径，不再内联全文，
    避免对写书有意义的成品被重复复制多次（下游按索引去读原文件，只读一份）。
    修订差异（调整稿）单独列在 _logs 下。"""
    import glob as _glob
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if st is None:
        return ""
    base = _project_ws()
    products, diffs = [], []
    for step in st["steps"]:
        sn = step["name"]
        for b in (step.get("blocks") or []):
            d = os.path.dirname(_produce_path(stage_key, sn, b))
            nm = os.path.basename(_produce_path(stage_key, sn, b))
            if stage_key in CHAPTER_AWARE_STAGES:
                hits = sorted(_glob.glob(os.path.join(d, f"第*章_{_safe_name(b)}.md")))
                if not hits:
                    hits = [os.path.join(d, nm)] if os.path.exists(os.path.join(d, nm)) else []
            else:
                hits = [os.path.join(d, nm)] if os.path.exists(os.path.join(d, nm)) else []
            for p in hits:
                products.append(os.path.relpath(p, base).replace("\\", "/"))
        # 该子步的修订差异稿（调整者输出，差异化内容）
        ap = _adjust_path(stage_key, sn)
        ad = os.path.dirname(ap)
        an = os.path.basename(ap)
        if stage_key in CHAPTER_AWARE_STAGES:
            dhits = sorted(_glob.glob(os.path.join(ad, f"第*章_{an}")))
            if not dhits:
                dhits = [ap] if os.path.exists(ap) else []
        else:
            dhits = [ap] if os.path.exists(ap) else []
        for p in dhits:
            diffs.append(os.path.relpath(p, base).replace("\\", "/"))
    L = [f"# 环节【{stage_key}】产出索引（供下游读取；成品仅此一份，修订差异见 _logs）", ""]
    if products:
        L.append("## 成品（对写书有意义，留在环节目录）")
        for x in products:
            L.append(f"- {x}")
        L.append("")
    if diffs:
        L.append("## 修订差异（操作类，存 _logs）")
        for x in diffs:
            L.append(f"- {x}")
        L.append("")
    return "\n".join(L)


def _resolve_context(ctx_path):
    """下游读取环节 context：若为『产出索引』则按索引逐个读原文件拼接（只读一份，避免重复）；
    否则（老项目全文格式）兼容返回原文。"""
    txt = _read(ctx_path)
    if "产出索引" in txt:
        base = _project_ws()
        out = []
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith("- ") and s.endswith(".md"):
                p = os.path.join(base, s[2:].strip())
                t = _read(p)
                if t and t.strip():
                    out.append(t)
        return "\n\n".join(out) if out else txt
    return txt


# ----------------------------------------------------------------- 真实产物校验（默认红，只有读取到真实文件才转绿）
# MOCK 模式下只验证文件已落盘且非空，方便流程测试时方块正常变绿；
# 真实模式下要求内容不少于 20 字节，避免被占位/空内容糊弄。
_REAL_MIN_BYTES = 1 if MOCK_PROMPTS else 20


def _item_artifact_path(stage_key, step_name, item, chapter, round=1):
    """返回某子项（块 / 审核者 / 调整者）对应的产物文件路径。

    round>=2 为「环节终审闭环」的复检轮次，审核意见/调整稿带 _第N轮 后缀。
    """
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if st is None:
        return None
    step = next((s for s in st["steps"] if s["name"] == step_name), None)
    if step is None:
        return None
    if item == "reviewer":
        return _review_path(stage_key, step_name, chapter, round)
    if item == "adjuster":
        return _adjust_path(stage_key, step_name, chapter, round)
    if item in step.get("blocks", {}):
        return _produce_path(stage_key, step_name, item, chapter)
    return None


# ----------------------------------------------------------------- 环节终审闭环
# 每个大环节的【最后一个子步】由「审核者 + 调整者」承担环节终审闭环：
#   1) 整合总结本环节全部产出；
#   2) 审核者给出「打钩清单」式弊病表（- [x] 达标 / - [ ] 未达标）；
#   3) 调整者按未打钩项逐条修改 → 改完必须再交审核者复审；
#   4) 只有审核清单全部打钩，调整者才交付；否则进入下一轮，最多 FINAL_LOOP_MAX_ROUNDS 轮。
FINAL_LOOP_MAX_ROUNDS = 3
# 审核者 / 调整者必须是本地端（非 web）AI：只有本地端能可靠读盘写盘、整合与重写大段文本。
REVIEWER_LOCAL_ONLY = True
ADJUSTER_LOCAL_ONLY = True

_UNCHECKED_RE = re.compile(r"^\s*[-*+]\s*\[\s*\]\s*\S", re.M)
_CHECKED_RE = re.compile(r"^\s*[-*+]\s*\[[xX]\]\s*\S", re.M)
_ALL_PASS_RE = re.compile(r"全部打钩|全部通过|无弊病|无需修改|可交付")

# 数字评分门槛：启用了 score_gate 的子步，审核者需给出『综合评分：X/10』，
# 平均分 ≥ 该门槛才视为达标（可配；默认 8）。低于则进入复审轮，直至达标或达最大轮次。
REVIEW_SCORE_THRESHOLD = 8.0
_SCORE_RE = re.compile(r"综合评分[：:]\s*(\d+(?:\.\d+)?)\s*/\s*10", re.I)


def stage_step_score_gate(stage_key, step_name):
    """返回该子步的数字评分门槛（float），未设则返回 None。"""
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st:
        return None
    step = next((s for s in st["steps"] if s["name"] == step_name), None)
    if not step:
        return None
    g = step.get("score_gate")
    if g is None:
        return None
    try:
        return float(g)
    except Exception:
        return None


def score_meets_threshold(text, threshold):
    """解析审核意见里的『综合评分：X/10』，判断平均分是否达标。"""
    if not text:
        return False
    m = _SCORE_RE.search(text)
    if not m:
        return False
    try:
        return float(m.group(1)) >= float(threshold)
    except Exception:
        return False


def _gate_passed(rtext, gate):
    """达标判定：打钩清单全过，或（设了数字门槛时）综合评分达标。"""
    if review_all_checked(rtext):
        return True
    if gate is not None and score_meets_threshold(rtext, gate):
        return True
    return False


def _SCORE_INSTR(gate):
    return ("\n\n## 评分要求（本环节启用数字评分门槛）\n"
            "请按以下八维逐维打分（每维 1-10 分）："
            "兼容、结构、衔接、角色、创意、节奏、文笔、落地。\n"
            "最后必须单独输出一行：综合评分：X/10（X 为八维平均分，保留 1 位小数）。\n"
            f"综合评分 ≥ {gate} 视为达标，结论可写『全部打钩，可交付』；"
            "低于则写『仍有 N 项未达标，需调整者修改』。"
            "评分需给出简要理由，不要只给数字。")


def last_step_name(stage_key):
    """本环节最后一个子步名（环节终审闭环的承载子步）。"""
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st or not st["steps"]:
        return None
    return st["steps"][-1]["name"]


def assemble_stage_material(stage_key, state, chapter=None):
    """汇总本环节【全部产出】（各子步的块产出 + 已有调整稿），供环节终审整合总结使用。"""
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if st is None:
        return ""
    parts = []
    for step in st["steps"]:
        sn = step["name"]
        for b in (step.get("blocks") or []):
            p = _produce_path(stage_key, sn, b, chapter)
            t = _read(p) if (p and os.path.exists(p)) else ""
            if t and t.strip():
                parts.append(f"# 【{sn}】{b}\n{t}")
        ap = _adjust_path(stage_key, sn, chapter)
        t = _read(ap) if (ap and os.path.exists(ap)) else ""
        if t and t.strip():
            parts.append(f"# 【{sn}】调整稿\n{t}")
    return "\n\n".join(parts)


def loop_round(rstate, stage_key, sn):
    """读取该子步当前的终审闭环轮次（从 1 开始）。"""
    try:
        return int(rstate["stages"][stage_key].get("loop_rounds", {}).get(sn, 1))
    except Exception:
        return 1


def set_loop_round(rstate, stage_key, sn, r):
    rstate["stages"][stage_key].setdefault("loop_rounds", {})[sn] = int(r)


def review_all_checked(text):
    """判定审核意见是否『全部打钩』。

    先按复选框清单判定（有 - [ ] → 未通过；全 - [x] → 通过）；
    清单缺失时回退看结论句（全部打钩/全部通过/无弊病/可交付）。
    都没有 → 判未通过（保守，继续下一轮或提示人工确认）。
    """
    if not text or not text.strip():
        return False
    unchecked = len(_UNCHECKED_RE.findall(text))
    checked = len(_CHECKED_RE.findall(text))
    if unchecked:
        return False
    if checked:
        return True
    return bool(_ALL_PASS_RE.search(text))


def local_ais_names():
    """本地端（类型 == electron）AI 名列表：优先『已启用』的，全都没启用才退回全部本地端。"""
    try:
        ps = _load_players() or []
        enabled = [e.get("名字") for e in ps
                   if e.get("名字") and e.get("类型") == "electron"
                   and e.get("启用", True) is not False]
        if enabled:
            return enabled
        return [e.get("名字") for e in ps
                if e.get("名字") and e.get("类型") == "electron"]
    except Exception:
        return []


def local_role_guard(ai, role, log_fn=print):
    """保证审核者/调整者是本地端 AI；被指派成 web 时自动替换为本地端。

    返回可用的本地 AI 名；没有本地端 AI 时返回 None（调用方应中止该任务）。
    """
    label = "审核者" if role == "reviewer" else "调整者"
    enforce = REVIEWER_LOCAL_ONLY if role == "reviewer" else ADJUSTER_LOCAL_ONLY
    if not enforce:
        return ai or None
    locals_ = local_ais_names()
    if not locals_:
        log_fn(f"⛔ 未配置本地端(非web)AI，{label}无法工作；请先在『添加AI』里添加本地端 AI。")
        return None
    if not ai:
        return locals_[0]
    if ai in locals_:
        return ai
    if _is_web(ai):
        log_fn(f"⚠ {label}「{ai}」是网页端，已按规则替换为本地端「{locals_[0]}」")
        return locals_[0]
    return ai


def _artifact_is_real(path):
    """文件存在且为真实产出（够大、且非 mock 连通性占位）才视为通过。"""
    if not path or not os.path.exists(path):
        return False
    try:
        sz = os.path.getsize(path)
    except Exception:
        return False
    if sz < _REAL_MIN_BYTES:
        return False
    # 真实模式下额外排除明显占位内容；MOCK 模式已由上面 min bytes=1 放行占位文件用于流程测试。
    if not MOCK_PROMPTS:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                head = f.read(400)
        except Exception:
            head = ""
        # 排除 dry / mock 演练占位（这些旧文件若被当成“真实产物”，会让环节误判通过并跳过重抓）
        for bad in ("连通性模拟", "dry 模拟产出", "网页端 模拟产出",
                    "dry-run 占位", "mock 占位", "非真实 AI 输出", "占位，非真实"):
            if bad in head:
                return False
        if head.strip() in ("你好", "你好。"):
            return False
    return True


# ----------------------------------------------------------------- 规划契约（初始化生成的 工作区/规划 蓝图）
def _plan_dir():
    """当前项目的『按项目』工作区规划目录（与产出目录同级：workspace/<项目>/规划）。"""
    ws = _project_ws()
    safe = os.path.basename(os.path.normpath(ws))
    return paths.workspace_project_path(safe, "规划")


def _plan_file_for(stage_key, step_name):
    """该子步的规划文件路径；不存在（老项目）返回 None，调用方退化为不校验。"""
    p = os.path.join(_plan_dir(), f"规划_{stage_key}_{step_name}.md")
    return p if os.path.exists(p) else None


def _norm_plan_name(n):
    """去掉章意识前缀（`第NNN章_` 或占位 `第{N}章_`）与反引号，便于规划文件名与实际文件名比对。"""
    n = n.strip().strip("`")
    return re.sub(r"^第(\d+|\{N\})章_", "", n)


def _plan_lists_output(plan_path, out_path):
    """规划『产出要求』是否列出该实际产出文件（容忍章号差异）。用于漂移检测。"""
    base = _norm_plan_name(os.path.basename(out_path))
    try:
        txt = _read(plan_path)
    except Exception:
        return True
    for line in txt.splitlines():
        if "执行产出" in line or "调整稿" in line:
            for seg in line.split("`"):
                if _norm_plan_name(seg) == base:
                    return True
    return False


def _plan_verify_pass(stage_key, step_name, item, out_path, log_fn):
    """子项通过后：引用规划并交叉校验产出是否被规划列为要求（漂移检测，仅警告不阻断）。"""
    plan_path = _plan_file_for(stage_key, step_name)
    if plan_path:
        log_fn(f"    📋 已对照规划校验：{os.path.basename(out_path)}")
        if item != "reviewer" and not _plan_lists_output(plan_path, out_path):
            log_fn(f"    ⚠ 规划未列出此产出（规划漂移？请核对）：{os.path.basename(out_path)}")
    return True


def _step_items_of(stage_key, step):
    """子步下的全部子项名（块 + reviewer/adjuster）。

    终审子步同样有 adjuster（终审闭环 = 审核 → 调整 → 复审），
    且带产出块的终审子步（如环节1·规划复核）还带全部并行块。
    """
    items = list(step.get("blocks", []) or [])
    items.extend(["reviewer", "adjuster"])
    return items


def _clear_stage_stale_fails(stage_key, rstate):
    """清除上一次运行遗留在该环节的 fail 标记。

    背景：任一子项失败会级联把后续所有子项置 fail；若不在重跑前清理，即使本轮全部产出
    正常，stage_failed_steps 仍会看到子步为 fail 而立刻中止本环节，导致环节永远跑不完。
    本轮若真的失败，运行过程中会再次级联，不会掩盖真实错误。
    """
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st:
        return 0
    cleared = 0
    for step in st["steps"]:
        sn = step["name"]
        for item in _step_items_of(stage_key, step):
            cur = (rstate["stages"][stage_key].get("item_status", {})
                   .get(sn, {}).get(item, "none"))
            if cur == "fail":
                set_item_status(rstate, stage_key, sn, item, "none")
                cleared += 1
    return cleared


def _assigned_ai(state, stage_key, sn, item):
    """子项是否已指派 AI；返回 AI 名或空串。"""
    cfg = (state.get(stage_key, {}).get("steps", {}) or {}).get(sn, {}) or {}
    if item == "reviewer":
        return cfg.get("reviewer") or ""
    if item == "adjuster":
        return cfg.get("adjuster") or ""
    return (cfg.get("blocks") or {}).get(item) or ""


def _verify_stage_from_disk(stage_key, state, rstate, chapter):
    """按磁盘真实产物复核本环节各子项状态：有真实文件→通过(绿)；原本通过但文件缺失→退回未通过(红)。

    未指派 AI 的子项视为「不涉及」直接通过，避免未配置就永久拦截放行。
    """
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st:
        return
    for step in st["steps"]:
        sn = step["name"]
        for item in _step_items_of(stage_key, step):
            if not _assigned_ai(state, stage_key, sn, item):
                # 未指派 AI：不涉及，按通过处理
                set_item_status(rstate, stage_key, sn, item, "pass")
                continue
            p = _item_artifact_path(stage_key, sn, item, chapter)
            _cur = (rstate["stages"][stage_key].get("item_status", {})
                    .get(sn, {}).get(item, "none"))
            # 手动判不通过（fail）的子项不被磁盘旧产物自动翻绿，需重新生成
            if _cur != "fail" and _artifact_is_real(p):
                set_item_status(rstate, stage_key, sn, item, "pass")
            else:
                cur = (rstate["stages"][stage_key].get("item_status", {})
                       .get(sn, {}).get(item, "none"))
                if cur == "pass":
                    set_item_status(rstate, stage_key, sn, item, "none")  # 假绿→退回红
                elif cur == "running":
                    # 上次中断残留的「生产中」→ 复位为未判定
                    set_item_status(rstate, stage_key, sn, item, "none")


def verify_chapter_from_disk(chapter):
    """复核整章（写作/去AI/审核/出厂）各子项状态，返回最新 run_state。"""
    state, rstate = load()
    ch = int(chapter) if chapter else get_current_chapter()
    for sk in CHAPTER_AWARE_STAGES:
        _verify_stage_from_disk(sk, state, rstate, ch)
    save(state, rstate)
    return rstate


# ----------------------------------------------------------------- 上游累积稿
def _init_context():
    """第 0 步初始化文件（项目信息 + 故事梗概 + AI 建议）作为环节1的上一环节产出。"""
    if not _PROJECT_WS:
        return ""
    init_dir = os.path.join(_PROJECT_WS, "00_初始化")
    parts = []
    mapping = {
        "项目信息": "项目信息.json",
        "故事梗概": "故事梗概.md",
        "AI建议调整方向": "AI建议调整方向.md",
    }
    for label, name in mapping.items():
        p = os.path.join(init_dir, name)
        if os.path.exists(p):
            parts.append(f"# {label}\n{_read(p)}")
    return "\n\n".join(parts)


def _upstream_text(stage_key):
    idx = STAGE_ORDER.index(stage_key)
    parts = []
    if idx == 0:
        init = _init_context()
        if init:
            parts.append(init)
    for sk in STAGE_ORDER[:idx]:
        c = _context_path(sk)
        if os.path.exists(c):
            parts.append(f"# 上游环节【{sk}】已产出内容\n" + _resolve_context(c))
    return "\n\n".join(parts)


# ----------------------------------------------------------------- 逐章循环（环节2起）
# 从「写作」环节开始，正文/去AI/审核/出厂 均按章循环：每章先读上一章内容，再生成本章。
# 文件命名带章号：02_写作/第001章_正文产出.md、03_去AI/第001章_朗读试读.md … 便于标注与追溯。
CHAPTER_AWARE_STAGES = ("写作", "去AI", "审核", "出厂")
# 各阶段中「按章循环」的子步；其余子步只跑一次（如 写作 的 章纲、终审）。
PER_CHAPTER_STEPS = {
    "写作": ["正文"],
    "去AI": ["去AI润色"],
    "审核": ["质检评审"],
    "出厂": ["出厂检查"],
}
# 上一环节链：用于取「同章待处理稿」（本章要处理的原始稿来自上一环节的同章产物）。
_STAGE_CHAIN = {"写作": None, "去AI": "写作", "审核": "去AI", "出厂": "审核"}

CHAPTER_COUNT = 1
CURRENT_CHAPTER = 1


def set_chapter_count(n):
    """设置本书计划章节数（来自项目信息「章节数」）。"""
    global CHAPTER_COUNT
    try:
        CHAPTER_COUNT = max(1, int(n))
    except Exception:
        CHAPTER_COUNT = 1


def _chapter_count():
    try:
        return max(1, int(CHAPTER_COUNT))
    except Exception:
        return 1


def set_current_chapter(n):
    global CURRENT_CHAPTER
    try:
        CURRENT_CHAPTER = max(1, int(n))
    except Exception:
        CURRENT_CHAPTER = 1


def get_current_chapter():
    try:
        return max(1, int(CURRENT_CHAPTER))
    except Exception:
        return 1


def get_chapter_total():
    return _chapter_count()


def _chapter_progress_path():
    return os.path.join(_project_ws(), "_collab_章节进度.json")


def load_chapter_progress():
    """从项目工作区读取章节进度（当前章 / 总章数）。"""
    global CURRENT_CHAPTER, CHAPTER_COUNT
    p = _chapter_progress_path()
    if os.path.exists(p):
        try:
            d = json.load(open(p, encoding="utf-8")) or {}
            set_current_chapter(d.get("current", 1))
            set_chapter_count(d.get("total", _chapter_count()))
        except Exception:
            pass
    return get_current_chapter(), get_chapter_total()


def save_chapter_progress():
    d = {"current": get_current_chapter(), "total": get_chapter_total()}
    _write(_chapter_progress_path(), json.dumps(d, ensure_ascii=False, indent=2))


def reset_chapter_cycle():
    """每章开始前重置章核心环节（写作/去AI/审核/出厂）的门控与子步状态，避免上一章的通过态残留。"""
    state, rstate = load()
    for sk in CHAPTER_AWARE_STAGES:
        rstate["stages"][sk]["status"] = "pending"
        items = rstate["stages"][sk].get("item_status", {})
        for sn, step in items.items():
            for it in list(step.keys()):
                step[it] = "none"
    rstate["current_stage"] = "写作"
    save(state, rstate)


def _chapter_text(stage_key, ch):
    """读取某环节某章的全部块产物（排除审核意见/调整稿），拼接为章内容。
    产物现已按子步分文件夹存放，故递归搜索子目录；同时排除「本步骤规划/下一步建议」等页级文档。"""
    d = _stage_dir(stage_key)
    out = []
    for f in sorted(glob.glob(os.path.join(d, "**", f"第{ch:03d}章_*.md"), recursive=True)):
        bn = os.path.basename(f)
        if bn.endswith("_审核意见.md") or bn.endswith("_调整稿.md"):
            continue
        if bn.endswith("本步骤规划.md") or bn.endswith("下一步建议.md"):
            continue
        t = _read(f)
        if t:
            out.append(f"# {bn}\n{t}")
    return "\n\n".join(out)


def _previous_chapter_text(stage_key, ch):
    if ch <= 1:
        return ""
    return _chapter_text(stage_key, ch - 1)


def _chapter_upstream(stage_key, ch, base_upstream):
    """构造本章任务的注入上下文：基础上游 + 上一章（同环节，连续性）+ 本章待处理稿（上一环节同章）。"""
    parts = [base_upstream] if base_upstream else []
    prev = _previous_chapter_text(stage_key, ch)
    if prev:
        parts.append(f"# 上一章（第{ch - 1:03d}章）内容\n{prev}")
    prev_stage = _STAGE_CHAIN.get(stage_key)
    if prev_stage:
        cur = _chapter_text(prev_stage, ch)
        if cur:
            parts.append(f"# 本章待处理稿（来自上一环节【{prev_stage}】第{ch:03d}章）\n{cur}")
    return "\n\n".join(parts)


# ----------------------------------------------------------------- 提示词模板
def _step_is_final(stage_key, step_name):
    try:
        st = next(s for s in PIPELINE if s["key"] == stage_key)
        step = next(s for s in st["steps"] if s["name"] == step_name)
        return bool(step.get("final"))
    except Exception:
        return False


def _prompt_template_path(stage_key, step_name, task_type, task_key=None):
    """返回提示词模板路径，兼容多种命名约定（不破坏已写好的备份提示词）。

    - 块：优先精确名（已做非法字符归一化）；其次按块名模糊匹配（如『正文产出』
      被拆成 动/始/成/显/终/通 多段文件），命中多个时返回路径列表供 _load 拼接。
    - 审核者/调整者：优先约定名 _审核者.md / _调整者.md；否则回退 *-审核.md / *-调整.md。
      终审(final)步骤额外优先 *_终审放行评审.md。
    返回单路径字符串；块命中多个时返回路径列表（供 _load 拼接）。
    """
    folder_idx = STAGE_ORDER.index(stage_key) + 1
    folder = f"{folder_idx:02d}_{stage_key}"
    d = paths.prompt_path(folder)
    if not os.path.isdir(d):
        return None
    primaries, globs = [], []
    if task_type == "block" and task_key:
        primaries.append(_block_file(stage_key, step_name, task_key))
        globs.append(f"*{_safe_name(task_key)}*.md")
    elif task_type == "reviewer":
        primaries.append("_审核者.md")
        if _step_is_final(stage_key, step_name):
            primaries.append("_终审放行评审.md")
            globs.append("*终审*.md")   # 终审子步优先命中 2-5_终审放行评审.md
        globs.append("*审核*.md")
    elif task_type == "adjuster":
        primaries.append("_调整者.md")
        globs.append("*调整*.md")
    else:
        return None
    for c in primaries:
        p = os.path.join(d, c)
        if os.path.exists(p):
            return p
    for g in globs:
        hits = sorted(glob.glob(os.path.join(d, g)))
        if hits:
            return hits if task_type == "block" else hits[0]
    return None


def _load_prompt_template(stage_key, step_name, task_type, task_key=None):
    r = _prompt_template_path(stage_key, step_name, task_type, task_key)
    if not r:
        return None
    if isinstance(r, list):  # 块被拆成多段文件：拼接后返回
        texts = [_read(p) for p in r if os.path.exists(p)]
        joined = "\n\n---\n\n".join(t for t in texts if t)
        return joined or None
    return _read(r)


def _load_project_info():
    if not _PROJECT_WS:
        return "（未设置项目工作区）"
    info_path = os.path.join(_PROJECT_WS, "00_初始化", "项目信息.json")
    if os.path.exists(info_path):
        try:
            with open(info_path, encoding="utf-8") as f:
                data = json.load(f)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"（读取项目信息失败：{e}）"
    return "（项目信息未找到）"


def _load_platform_rules():
    p = paths.docs_path("平台规则.md")
    if os.path.exists(p):
        return _read(p)
    return "（暂无额外平台规则；请遵循通用网文平台规范。）"


def _fill_prompt(template, material=None, review=None):
    text = template
    text = text.replace("{{项目信息}}", _load_project_info())
    text = text.replace("{{上一环节产出}}", material or "（无）")
    text = text.replace("{{审核意见}}", review or "（无）")
    text = text.replace("{{平台规则}}", _load_platform_rules())
    return paths.replace_placeholders(text)


# ----------------------------------------------------------------- 指令构造
def _block_prompt(stage_key, step_name, block, upstream, dry):
    # 环节1·规划复核：块不是「从零生成」，而是对环节0.5 已生成的对应规划蓝图
    # （00_初始化/<block>.md）做「审核 / 评估 / 建议 / 调整」四件事，输出修订后的完整文件。
    if stage_key == "规划":
        # 不粘贴正文：直接给 AI 真实文件路径，让它自己读文件（网页版 AI 也贴不下大段内容）。
        src = os.path.join(_project_ws(), "00_初始化", block + ".md")   # 0.5 生成的基础稿
        out_dir = _stage_dir(stage_key)                                   # 本环节规划产出目录
        out_path = _produce_path(stage_key, step_name, block)            # 本块复核稿落盘路径
        head = (
            "【任务：环节1·规划 / 子步 %s / 块「%s」】\n" % (step_name, block)
            + "你是本环节的指定执行者，负责对本规划块做【深度审核 + 补全 + 深挖 + 完善】。"
            + "你不是只挑毛病，而是要把这份规划真正做扎实、做深、做完整。\n"
            + "请勿等待我粘贴正文——资料都在下面的文件里，直接打开读取：\n"
            + "  · 本块待完善的基础稿（必读）：%s\n" % src
            + "  · 本环节规划产出目录（可打开查看其他块的已复核稿，保持口径一致）：%s\n" % out_dir
            + "然后针对该块做以下工作：\n"
            + "  1) 深度审核：逐条核查逻辑 / 设定 / 人设 / 结构 / 卖点是否成立、"
            + "有无漏洞 / 矛盾 / 与 0.5 其他块口径冲突；\n"
            + "  2) 补全缺失：找出原稿没写清、写浅、或完全缺失的关键内容，主动补齐"
            + "（不回避、不略过，宁多勿缺）；\n"
            + "  3) 深挖建设：在原有方向上做方向性深化——本块若涉及定位 / 卖点，"
            + "须给出可落地的定位结论与卖点方向性建设；若涉及人物 / 世界观 / 结构 / 卷纲，"
            + "须给出更具体、可执行、有层次的深化方案；\n"
            + "  4) 完善成稿：直接输出【深度完善后的完整文件】——保留并强化原有合理部分，"
            + "整合上述补全与深挖，篇幅与深度应明显优于原稿，而非仅做微调。\n"
            + "任务重点关键词：「%s」——围绕该主题做方向性建设。\n" % block
            + "可附一段『修订说明』说明本次补全 / 深挖了什么。\n"
            + "完成后请把修订后的【完整文件】保存为（或写入）：\n  %s\n" % out_path
            + "（输出即作为「%s」的深度完善稿，将进入审核者综合评判与调整者最终调整闭环。）\n" % block
        )
        # 不再内联粘贴上游其它块内容；如需口径一致，AI 自行从上面的产出目录读取。
        return _fill_prompt(head)
    template = _load_prompt_template(stage_key, step_name, "block", block)
    if template:
        return _fill_prompt(template, material=upstream)
    st = next(s for s in PIPELINE if s["key"] == stage_key)
    label = st["label"]
    desc = st.get("desc", "")
    cmd = os.path.join(CMD_ROOT, stage_key, f"{block}.txt")
    if os.path.exists(cmd):
        core = _read(cmd)
    else:
        core = (f"你负责【{label}】环节的「{block}」部分。\n"
                f"环节说明：{desc}\n请产出该部分完整、可直接使用的内容。")
    head = (f"【任务：{label} / 子步 {step_name} / 块「{block}」】\n"
            f"{core}\n")
    body = ""
    if upstream and upstream.strip():
        body = ("\n==== 上游累积稿（含本环节已完成的块，请充分参考、保持连贯，勿重复已有内容）====\n"
                + upstream + "\n==== 上游结束 ====\n")
    return head + body


def _loop_head(role, round):
    """环节终审闭环的指令头：round>=2 为复检轮，要求对照上一轮清单复核。"""
    base = ("【环节终审闭环 · %s】\n"
            "你要对本环节【全部产出】负责：先做「本环节整合总结」，再按打钩清单逐条判定/修改。\n"
            "- 审核者：每条弊病必须写成 `- [ ] 未达标项 …` 或 `- [x] 已达标项 …`，"
            "结论写明「全部打钩，可交付」或「仍有 N 项未打钩，需调整者修改」。\n"
            "- 调整者：先整合总结，再逐条修好 `- [ ]` 项，稿末附「修改对照表」；"
            "改完必须交审核者复审，全部打钩后才交付。\n"
            % ("审核者" if role == "reviewer" else "调整者"))
    if round and int(round) >= 2:
        base += (f"\n【第 {int(round)} 轮复检】上一轮仍有未打钩项。"
                 f"请对照上一轮清单逐条复核：已修好的改为 `- [x]`，"
                 f"仍不合格的保留 `- [ ]` 并补充说明。\n")
    return base + "\n"


def _review_prompt(stage_key, step_name, material, round=1):
    gate = stage_step_score_gate(stage_key, step_name)
    template = _load_prompt_template(stage_key, step_name, "reviewer")
    if template:
        head = _loop_head("reviewer", round)
        if gate is not None:
            head += _SCORE_INSTR(gate)
        if stage_key == "规划":
            # 不粘贴 7 份块正文：给规划产出目录路径，让审核者自行读文件
            folder = _stage_dir(stage_key)
            review_path = _review_path(stage_key, step_name, None, round)
            note = ("\n\n【资料来源·请勿等待粘贴】本环节 7 份块复核稿均在目录：\n  %s\n"
                    "直接打开该目录下的文件读取即可。任务重点关键词：「环节1·规划综合审核」——"
                    "整合总结本环节全部产出是否自洽、完整、可进正文，按八方向逐条评判，"
                    "并给出『综合评分：X/10』（平均分≥%s 才达标）。\n"
                    "完成后请把审核意见保存为：\n  %s\n"
                    % (folder, gate if gate is not None else 8.0, review_path))
            return head + _fill_prompt(template + note, material=folder)
        return head + _fill_prompt(template, material=material)
    base = _loop_head("reviewer", round) + build_review_prompt(stage_key, step_name, "作品", material)
    if gate is not None:
        base += _SCORE_INSTR(gate)
    return base


def _adjust_prompt(stage_key, step_name, material, review, dry, round=1):
    template = _load_prompt_template(stage_key, step_name, "adjuster")
    # 差异化输出指令：调整者只写「与待修改稿有差异的部分」，避免同一份内容被重复复制多份
    diff_instr = ("\n\n## 输出要求（关键）\n"
                  "你只需输出【与待修改稿有差异的部分】：逐条列出你具体改了什么、改成什么"
                  "（修订项 / 差异点 / diff），【不要复述未改动的内容，不要输出完整稿】。"
                  "这样下游步骤只需读取原稿 + 你的差异，同一份内容不会被重复存储多份。\n")
    if template:
        head = _loop_head("adjuster", round) + diff_instr
        if stage_key == "规划":
            # 不粘贴待修改稿与审核意见：给目录路径与审核意见文件路径，让调整者自行读文件
            folder = _stage_dir(stage_key)
            review_path = _review_path(stage_key, step_name, None, round)
            adjust_path = _adjust_path(stage_key, step_name, None, round)
            note = ("\n\n【资料来源·请勿等待粘贴】待修改稿（7 份块复核稿）位于目录：\n  %s\n"
                    "对应的审核意见（第 %d 轮）位于：\n  %s\n"
                    "直接打开这些文件读取。任务重点关键词：「环节1·规划最终调整」——"
                    "严格按审核意见逐条修改，并【直接覆盖写回】原 7 份块文件（%s 下的 1-N_*.md，"
                    "就地更新为最终修正版）；回复里只给『修订对照表（仅列出你改动的点）』，"
                    "不要另存一份全量汇编稿。你的回复（差异对照表）会保存为：\n  %s\n"
                    % (folder, round, review_path, folder, adjust_path))
            return head + _fill_prompt(template + note, material=folder, review=review_path)
        return head + _fill_prompt(template, material=material, review=review)
    head = ("【修改任务】下面是一份待修改稿与对应的评审意见。"
            "请严格按评审意见逐条修改，但【只输出与待修改稿有差异的部分（具体修订项/改动点），"
            "不要复述未改动内容，不要输出完整稿】。\n")
    body = (f"\n=== 待修改稿 ===\n{material}\n\n=== 评审意见 ===\n{review}\n")
    return _loop_head("adjuster", round) + diff_instr + head + body


# ----------------------------------------------------------------- 本步骤规划 / 下一步建议
def _pick_stage_ai(state, stage_key):
    """挑一个本环节已指派的 AI 用于生成规划/建议文档；都没有则返回 None。"""
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st:
        return None
    for step in st["steps"]:
        sn = step["name"]
        blocks = state[stage_key]["steps"][sn]["blocks"]
        for _b, ai in blocks.items():
            if ai:
                return ai
        reviewer = state[stage_key]["steps"][sn].get("reviewer")
        if reviewer:
            return reviewer
        adjuster = state[stage_key]["steps"][sn].get("adjuster")
        if adjuster:
            return adjuster
    return None


def _step_plan_prompt(stage_key, state):
    """本环节执行规划文档（写给本环节目录的 本步骤规划.md）。"""
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st:
        return "请输出本步骤规划。"
    lines = [f"# 本步骤（环节【{st['label']}】）执行规划", st.get("desc", ""), ""]
    for step in st["steps"]:
        sn = step["name"]
        blocks = state[stage_key]["steps"][sn]["blocks"]
        reviewer = state[stage_key]["steps"][sn].get("reviewer")
        adjuster = state[stage_key]["steps"][sn].get("adjuster")
        lines.append(f"## 子步：{sn}" + ("（终审）" if step.get("final") else ""))
        if blocks:
            lines.append("产出块与指派：")
            for b, ai in blocks.items():
                lines.append(f"  - {b}  ←  {ai or '（未指派）'}")
        lines.append(f"审核者：{reviewer or '（无）'}；调整者：{adjuster or '（无）'}")
        lines.append("")
    if stage_key in CHAPTER_AWARE_STAGES:
        N = _chapter_count()
        lines.append(f"## 逐章循环（共 {N} 章）")
        lines.append(f"本环节从「写作」起按章循环：每个子步对第 1…{N} 章依次执行，"
                     f"产物文件以「第NNN章_」前缀标注章号（如 第001章_正文产出.md）。")
        lines.append("每章生成前会注入：基础上游（梗概/章纲/上一环节上下文）+ 上一章内容"
                     "（同环节连续性）+ 本章待处理稿（上一环节同章产物）。")
        lines.append("")
    plan = "\n".join(lines)
    return ("【任务：为本环节编写「本步骤规划」文档】\n"
            "你是本项目的总策划。请基于下面的环节定义与角色指派，输出一份 Markdown 规划说明，"
            "包含：本环节目标、每个子步要产出的内容、质量要点、子步间依赖、需要的上游输入。"
            "不要创作小说正文，只做规划与交接说明。\n\n"
            f"{plan}\n\n完成后请把完整结果写入你被指定的文件路径（不要只贴在聊天里）。")


def _next_step_advice_prompt(stage_key, state):
    """下一步建议文档（写给本环节目录的 下一步建议.md）。"""
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st:
        return "请输出下一步建议。"
    ctx = _read(_context_path(stage_key))
    idx = STAGE_ORDER.index(stage_key)
    if idx + 1 < len(STAGE_ORDER):
        nxt = STAGE_ORDER[idx + 1]
        nst = next((s for s in PIPELINE if s["key"] == nxt), None)
        nxt_desc = (f"下一环节【{nst['label']}】说明：{nst.get('desc', '')}\n"
                    f"其子步：{', '.join(x['name'] for x in nst['steps'])}")
    else:
        nxt_desc = "已是最后一个环节；请输出整体收尾、发布与上架的注意事项。"
    return ("【任务：编写「下一步建议」文档】\n"
            f"本环节【{st['label']}】已产出以下内容（累积摘要）：\n"
            f"{ctx[:3000]}\n\n"
            f"{nxt_desc}\n\n"
            "请输出一份 Markdown「下一步建议」：指出下一环节需要重点关注的输入、易错点、"
            "本环节成果如何被下游使用、以及对下一环节的具体交接建议。不要创作正文。\n"
            "完成后把完整结果写入你被指定的文件路径（不要只贴在聊天里）。")


# ----------------------------------------------------------------- 单任务发送（接入 mix_send）
def _is_web(ai):
    """该 AI 是否为网页端（无法自写文件，需从页面抓取回复）。"""
    try:
        for e in _load_players():
            if e.get("名字") == ai:
                return e.get("类型") == "web"
    except Exception:
        pass
    return False


def _capture_and_save(ai, out_path, log_fn, timeout):
    """网页端：轮询页面抓取 AI 回复，待「真实助手消息气泡」文本稳定后写入 out_path。
    n==0 表示只抓到整页回退文本（如网页原有内容/欢迎语），不算真正回复，避免没发送成功
    还误判为完成。"""
    log_fn(f"    🔍 {ai} 为网页端：等待回复生成并从页面抓取…")
    prev = ""
    stable = 0
    ever_real = False
    t0 = time.time()
    while time.time() - t0 < timeout:
        if _STOP:
            log_fn(f"    ⏸ {ai} 收到停止信号")
            break
        meta = _mix_capture(ai) or {}
        txt = (meta.get("text", "") or "").strip()
        n = meta.get("n", 0)
        if txt and n > 0:
            ever_real = True
            if txt == prev:
                stable += 1
            else:
                stable = 0
                prev = txt
            log_fn(f"    · 抓取中（助手气泡 {n} 个，{len(prev)} 字符，稳定 {stable}）")
            if stable >= 2:   # 约 8s 内容不变，视为生成完毕
                _write(out_path, prev)
                log_fn(f"    ✅ 已从页面抓取真实回复并保存（{len(prev)} 字符）→ {os.path.basename(out_path)}")
                return prev
        elif txt and n == 0:
            log_fn("    · 本轮仅抓到整页回退文本（无助手气泡），继续等待 AI 回复…")
        else:
            log_fn(f"    · 本轮未抓到文本，继续等待…")
        time.sleep(4)
    if ever_real and prev.strip():
        _write(out_path, prev)
        log_fn(f"    ⚠ {ai} 抓取超时，已保存最后抓到的回复（{len(prev)} 字符）→ {os.path.basename(out_path)}")
        return prev
    if not ever_real:
        log_fn(f"    ❌ {ai} 始终未出现助手回复（n==0，可能粘贴未成功或页面结构变化），不生成产出")
    else:
        log_fn(f"    ❌ {ai} 未能从页面抓取到回复（请确认该网页端已登录且 CDP 端口正确）")
    return ""
    return ""


# ----------------------------------------------------------------- 发送 / 落盘稳定性与容错
SEND_TIMEOUT = 60      # 单次发送调用（CDP/pyautogui）最长阻塞秒数；超过视为窗口假死
RESEND_MAX = 2         # 发送或写盘超时后，最多补发次数
STABLE_NEED = 3        # 本地端落盘：文件大小连续稳定次数（每次轮询 POLL_SEC 秒，≈15s）才判定完成
POLL_SEC = 5           # 落盘轮询间隔（秒）


def _artifact_exists(out_path, min_size):
    """精确路径优先；模拟模式下 AI 可能把产物写进块同名子目录，也一并接受。"""
    if os.path.exists(out_path) and os.path.getsize(out_path) >= min_size:
        return out_path
    block_dir = os.path.splitext(out_path)[0]
    if MOCK_PROMPTS and os.path.isdir(block_dir):
        # 必须目录树里存在“非空文件”才算真正产出，避免空目录被误判通过
        for root, dirs, files in os.walk(block_dir):
            for f in files:
                fp = os.path.join(root, f)
                if os.path.isfile(fp) and os.path.getsize(fp) >= min_size:
                    return fp
    return None


def _accept_artifact(out_path, art, log_fn):
    if art and art != out_path:
        try:
            import shutil
            shutil.copyfile(art, out_path)
        except Exception:
            pass
    try:
        sz = os.path.getsize(out_path)
    except Exception:
        sz = 0
    log_fn(f"    ✅ 已收到 {os.path.basename(out_path)}（{sz} 字节，已稳定），确认通过，进入下一项")
    return _read(out_path)


def _cdp_port_alive(port, timeout=2):
    """探测本地 CDP 调试端口是否可连。"""
    import socket
    try:
        with socket.create_connection(("127.0.0.1", int(port)), timeout=timeout):
            return True
    except Exception:
        return False


def _try_relaunch_ai(ai, log_fn):
    """发送失败时，若该本地 AI 的 CDP 端口不通，尝试带调试端口拉起一次并等待就绪。

    典型场景：WorkBuddy 压根没在运行（或上次没带 --remote-debugging-port 启动），
    CDP 连接超时 → 这里自动带端口启动并等端口就绪，让上层重试发送一次。
    若端口本来就通（窗口假死等），拉起无意义，返回 False 交由上层补发逻辑处理。
    """
    try:
        from players import load_players as _lp, launch as _launch
        cfg = next((p for p in _lp() if p.get("名字") == ai), None)
    except Exception:
        return False
    if not cfg or cfg.get("类型") != "electron":
        return False
    port = cfg.get("cdp_port")
    if not port or _cdp_port_alive(port):
        return False
    log_fn(f"    🚀 {ai} 调试端口 {port} 不通，尝试带 CDP 启动 {ai}…")
    try:
        _launch(cfg)
    except Exception as e:
        log_fn(f"    ⚠ 启动 {ai} 失败：{e}")
        return False
    for _ in range(30):
        if _cdp_port_alive(port):
            log_fn(f"    ✅ {ai} 已带 CDP 启动（端口 {port}），准备重试发送")
            return True
        time.sleep(1)
    log_fn(f"    ❌ {ai} 启动后端口 {port} 仍连不上："
           f"很可能是该软件已在运行但未带调试端口，请完全退出 {ai} 后重试")
    return False


def _send_once(ai, directive, log_fn):
    """调用 mix_send.send，带超时保护；返回 True/False（明确成败）或 None（发送层超时/假死）。"""
    box, err = {}, {}
    def _t():
        try:
            box["r"] = _mix_send(ai, directive)
        except Exception as _e:
            err["e"] = _e
    th = threading.Thread(target=_t, daemon=True)
    th.start()
    th.join(SEND_TIMEOUT)
    if th.is_alive():
        log_fn(f"    ❌ {ai} 发送调用超过 {SEND_TIMEOUT}s 未返回（窗口可能假死），将尝试补发")
        return None
    if "e" in err:
        log_fn(f"    ❌ {ai} 发送异常: {err['e']}")
        return False
    r = box.get("r")
    ok = bool(r) and (str(r).lstrip().startswith("✅")
                      or "已发送" in str(r)
                      or str(r).strip().lower().startswith("ok")
                      or "pyautogui ok" in str(r))
    if not ok:
        log_fn(f"    ❌ {ai} 发送未成功（{r}），跳过等待并标记该块失败")
        # CDP 连不上（AI 未运行/未带调试端口）→ 自动带端口拉起并重试一次
        if _try_relaunch_ai(ai, log_fn):
            log_fn(f"    🔁 重试发送 → {ai}")
            try:
                r2 = _mix_send(ai, directive)
            except Exception as _e2:
                r2 = f"❌ 重试异常 {_e2}"
            ok = bool(r2) and (str(r2).lstrip().startswith("✅")
                               or "已发送" in str(r2)
                               or str(r2).strip().lower().startswith("ok")
                               or "pyautogui ok" in str(r2))
            if ok:
                log_fn(f"    ✅ 重试发送成功：{r2}")
            else:
                log_fn(f"    ❌ 重试发送仍未成功（{r2}）")
    return ok


def _dispatch_send(ai, directive, log_fn):
    """发送并支持超时补发：True=已成功发送；False=明确失败（不再重试）；None=仍超时。"""
    res = _send_once(ai, directive, log_fn)
    if res is True or res is False:
        return res
    for _i in range(1, RESEND_MAX + 1):
        if _STOP:
            return False
        log_fn(f"    🔁 发送超时，补发第 {_i}/{RESEND_MAX} 次 → {ai}")
        res = _send_once(ai, directive, log_fn)
        if res is True:
            return True
        if res is False:
            return False
    return None


def _collect_local(ai, directive, out_path, log_fn, timeout, min_size):
    """本地端：发送 → 轮询文件大小「连续稳定」判定完成；写盘超时则补发后再等，避免误收半截稿。"""
    if _dispatch_send(ai, directive, log_fn) is not True:
        return ""
    log_fn(f"    ⏳ 等待 {ai} 生成并写盘 {os.path.basename(out_path)}（需大小连续稳定 {STABLE_NEED} 次）…")
    t0 = time.time()
    last_size, stable = -1, 0
    while time.time() - t0 < timeout:
        if _STOP:
            log_fn(f"    ⏸ {ai} 收到停止信号")
            return _read(out_path) if os.path.exists(out_path) else ""
        if _PAUSE:
            time.sleep(2)          # 暂停期间冻结超时计时
            t0 = time.time()
            continue
        art = _artifact_exists(out_path, min_size)
        if art is not None:
            try:
                sz = os.path.getsize(out_path)
            except Exception:
                sz = 0
            if sz >= min_size and sz == last_size:
                stable += 1
            else:
                stable = 0
                last_size = sz
            if stable >= STABLE_NEED:
                return _accept_artifact(out_path, art, log_fn)
        time.sleep(POLL_SEC)
    # 等待写盘超时：补发后最多再等一轮
    for _i in range(1, RESEND_MAX + 1):
        if _STOP or _PAUSE:
            break
        log_fn(f"    ⏱ {ai} 等待写盘超时，补发第 {_i}/{RESEND_MAX} 次…")
        if _dispatch_send(ai, directive, log_fn) is not True:
            break
        t0 = time.time()
        last_size, stable = -1, 0
        while time.time() - t0 < min(timeout, 300):
            if _STOP:
                return _read(out_path) if os.path.exists(out_path) else ""
            if _PAUSE:
                time.sleep(2); t0 = time.time(); continue
            art = _artifact_exists(out_path, min_size)
            if art is not None:
                try:
                    sz = os.path.getsize(out_path)
                except Exception:
                    sz = 0
                if sz >= min_size and sz == last_size:
                    stable += 1
                else:
                    stable = 0; last_size = sz
                if stable >= STABLE_NEED:
                    return _accept_artifact(out_path, art, log_fn)
            time.sleep(POLL_SEC)
    # 最终超时收尾：模拟模式下若 AI 已建立目录结构（但无文本），仍放行但明确警告
    block_dir = os.path.splitext(out_path)[0]
    if MOCK_PROMPTS and os.path.isdir(block_dir):
        tree = []
        for root, dirs, files in os.walk(block_dir):
            rel = os.path.relpath(root, block_dir)
            for f in files:
                tree.append(f if rel == "." else os.path.join(rel, f))
        summary = ("你好\n\n[连通性模拟] AI 已建立目录产物（无文本内容），结构：\n"
                   + "\n".join("  - " + t for t in tree) + "\n")
        _write(out_path, summary)
        log_fn(f"    ⚠ {os.path.basename(out_path)} 仅建立目录结构（无文本内容），按连通性模拟放行：{block_dir}")
        return _read(out_path)
    log_fn(f"    ⚠ {ai} 超时未写盘（含 {RESEND_MAX} 次补发），该块标记失败")
    return _read(out_path) if os.path.exists(out_path) else ""


def _do_task(ai, text, out_path, log_fn, dry, timeout=600):
    """发送一个任务给 ai，并取回其写盘产物。dry 模式直接落占位。

    真实模式：调用 windows-use/mix_send.send(ai, directive) 把任务投到对应 AI 窗口，
    AI 按要求把结果写入 out_path，本函数轮询该文件作为回执。
    关键稳定性改进：发送调用带超时保护、写盘需「大小连续稳定」才判定完成、超时自动补发、
    等待期间尊重暂停（冻结超时计时），避免误收半截稿 / 窗口假死卡线程 / 超时丢进度。
    """
    # 先建好产物所在文件夹，确保真实模式 AI 能直接落盘到 out_path
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    except Exception:
        pass
    min_size = 1 if MOCK_PROMPTS else 50
    # 连通性模拟时，AI 落盘很快；把等待超时收到 180s，避免某块异常时长时间空等
    if MOCK_PROMPTS:
        timeout = min(timeout, 180)

    art = _artifact_exists(out_path, min_size)
    if not dry and art is not None:
        log_fn(f"    ↺ {ai} 已有产物，跳过（{os.path.basename(out_path)}）")
        return _accept_artifact(out_path, art, log_fn)
    # 网页端 AI 无法自写文件：改用「从页面抓取回复」方式落盘
    ai_is_web = _is_web(ai)

    # 连通性模拟：真实投递，但只发极简指令，避免消耗 AI
    if MOCK_PROMPTS and not ai_is_web:
        text = (f"【连通性模拟-请勿消耗】请创建/写入文件「{os.path.basename(out_path)}」"
                f"（完整路径：{out_path}）。\n文件内容只需一行：你好\n"
                f"不要做任何额外创作，也不要输出其它内容。"
                f"注意：请直接在该路径写成一个 .md 文件，不要新建子文件夹。")
        log_fn(f"    [mock] {ai}: 连通性模拟指令 -> {os.path.basename(out_path)}")
    elif MOCK_PROMPTS and ai_is_web:
        # 网页端模拟：不真正抓取，直接写占位回复（仅用于连通性/流程测试）
        content = f"【{ai} 网页端 模拟产出】\n{text[:240]}\n（mock 占位，非真实 AI 输出）"
        _write(out_path, content)
        log_fn(f"    [mock-web] {ai}: 模拟产出 -> {os.path.basename(out_path)}")
        return content
    if dry and not MOCK_PROMPTS:
        content = f"【{ai} dry 模拟产出】\n{text[:240]}\n（dry-run 占位，非真实 AI 输出）"
        _write(out_path, content)
        log_fn(f"    [dry] {ai}: 模拟产出 -> {os.path.basename(out_path)}")
        return content

    # 真实/网页端发送指令
    if ai_is_web:
        directive = (text + "\n\n【重要】请把你的完整结果【原样、不省略】直接回复在本对话里"
                           "（不要只给摘要，也不要写成文件）；回答结束即可。")
    else:
        directive = (text + f"\n\n【重要】完成后，请把你的完整结果【原样、不省略】写入文件：\n"
                     f"{out_path}\n（用文件方式保存，不要只贴在聊天里）")

    if ai_is_web:
        # 网页端：发送后从页面抓取回复并保存（_capture_and_save 内部已含稳定判定与超时）
        if _dispatch_send(ai, directive, log_fn) is not True:
            return ""
        return _capture_and_save(ai, out_path, log_fn, timeout)
    # 本地端：发送 → 等待文件写入「稳定」→（写盘超时则补发）→ 推进
    return _collect_local(ai, directive, out_path, log_fn, timeout, min_size)


# ----------------------------------------------------------------- 单子步
def _run_step(stage_key, step, state, rstate, upstream, log_fn, dry, refresh_fn=None, chapter=None):
    sn = step["name"]
    final = bool(step.get("final"))
    blocks = state[stage_key]["steps"][sn]["blocks"]
    reviewer = state[stage_key]["steps"][sn]["reviewer"]
    adjuster = state[stage_key]["steps"][sn]["adjuster"]
    ch_tag = f" 第{chapter:03d}章" if chapter else ""
    log_fn(f"  · 子步[{sn}]{ch_tag}（{'终审' if final else '常规'}）")
    plan_ref = _plan_file_for(stage_key, sn)
    if plan_ref:
        log_fn(f"  📋 执行前读取规划契约：{plan_ref}")

    def _refresh():
        if refresh_fn:
            refresh_fn()

    def _path(item):
        return _item_artifact_path(stage_key, sn, item, chapter,
                                   loop_round(rstate, stage_key, sn))

    def _skip_if_done(item):
        """已存在真实产物则直接通过（绿），跳过重发；返回其文本表示已跳过。

        被手动判不通过（fail）的子项不跳过——必须重新生成。
        """
        _cur = (rstate["stages"][stage_key].get("item_status", {})
                .get(sn, {}).get(item, "none"))
        if _cur != "fail" and _artifact_is_real(_path(item)):
            txt = _read(_path(item))
            set_item_status(rstate, stage_key, sn, item, "pass")
            save(state, rstate)
            _refresh()
            log_fn(f"    ↺ 子项「{item}」已存在真实产物，跳过重发（绿）")
            return txt
        return None

    def _halted():
        if _STOP or _PAUSE:
            log_fn("⏸ 收到暂停/停止，不再发送后续内容")
            _refresh()
            return True
        return False

    # 1) 产出（同子步内块串行：后续块必须等前一块完成，并把前面块的产出注入提示词）
    outs = []
    running_upstream = upstream
    for block, ai in blocks.items():
        if _halted():
            return ""
        if not ai:
            log_fn(f"    ⏭ 块「{block}」未指派 AI，视为不涉及，跳过")
            continue
        done = _skip_if_done(block)
        if done is not None:
            block_text = f"# {block}\n{done}"
            outs.append(block_text)
            running_upstream = (running_upstream + "\n\n" + block_text) if running_upstream else block_text
            continue
        # 标记为生产中（黄点），供 UI 状态圆点展示
        set_item_status(rstate, stage_key, sn, block, "running")
        save(state, rstate)
        _refresh()
        instr = _block_prompt(stage_key, sn, block, running_upstream, dry)
        out = _do_task(ai, instr, _produce_path(stage_key, sn, block, chapter), log_fn, dry)
        if not (out and out.strip()):
            log_fn(f"    ✖ 块「{block}」产出为空，子步中断")
            cascade_fail_from_item(rstate, stage_key, sn, block)
            save(state, rstate)
            _refresh()
            return ""
        # 必须读取生成的真实文件、且为真实内容，才标记通过（绿）；否则保持红
        if not _artifact_is_real(_produce_path(stage_key, sn, block, chapter)):
            log_fn(f"    ⚠ 块「{block}」未生成真实文件，保持未通过（红）")
            save(state, rstate)
            _refresh()
            return ""
        set_item_status(rstate, stage_key, sn, block, "pass")
        save(state, rstate)
        log_fn(f"    ✔ 块「{block}」通过（已读取真实文件）")
        _plan_verify_pass(stage_key, sn, block, _produce_path(stage_key, sn, block, chapter), log_fn)
        _refresh()
        block_text = f"# {block}（由 {ai} 产出）\n{out}"
        outs.append(block_text)
        running_upstream = (running_upstream + "\n\n" + block_text) if running_upstream else block_text
    assembled = "\n\n".join(outs) if outs else ""
    material = assembled or upstream  # 终审/无块时以累积稿为评审对象

    # 环节终审：最后一个子步承担「整合总结 + 打钩闭环」，评审材料用本环节全部产出
    is_stage_final = (sn == last_step_name(stage_key))
    if is_stage_final:
        sm = assemble_stage_material(stage_key, state, chapter)
        if sm.strip():
            material = sm
            log_fn(f"    🧩 环节终审：已整合本环节全部产出（{len(sm)} 字符）")
    # 审核者 / 调整者必须是本地端 AI（网页端无法可靠读盘写盘、整合重写大段文本）
    reviewer = local_role_guard(reviewer, "reviewer", log_fn)
    adjuster = local_role_guard(adjuster, "adjuster", log_fn)
    # 数字评分门槛（仅启用了 score_gate 的子步生效，如环节1·规划复核）
    gate = stage_step_score_gate(stage_key, sn)

    # 2) 审核 + 修改 + 环节终审闭环（审核 → 调整 → 复审 → 全部打钩才交付）
    def _run_review(rnd):
        """第 rnd 轮审核。返回 (审核文本, 是否成功)。"""
        if _halted():
            return "", False
        done = _skip_if_done("reviewer")
        if done is not None:
            return done, True
        set_item_status(rstate, stage_key, sn, "reviewer", "running")
        save(state, rstate)
        _refresh()
        p = _review_path(stage_key, sn, chapter, rnd)
        rev = _do_task(reviewer, _review_prompt(stage_key, sn, material, rnd), p, log_fn, dry)
        if not (rev and rev.strip()):
            log_fn(f"    ✖ 审核（第{rnd}轮）为空，子步中断")
            cascade_fail_from_item(rstate, stage_key, sn, "reviewer")
            save(state, rstate)
            _refresh()
            return "", False
        if not _artifact_is_real(p):
            log_fn(f"    ⚠ 审核（第{rnd}轮）未生成真实文件，保持未通过（红）")
            save(state, rstate)
            _refresh()
            return "", False
        set_item_status(rstate, stage_key, sn, "reviewer", "pass")
        save(state, rstate)
        log_fn(f"    ✔ {'终审' if final else '审核'}通过（第{rnd}轮 / {reviewer}）")
        _plan_verify_pass(stage_key, sn, "reviewer", p, log_fn)
        _refresh()
        return rev, True

    def _run_adjust(rnd, rev_text):
        if _halted():
            return "", False
        done = _skip_if_done("adjuster")
        if done is not None:
            return done, True
        set_item_status(rstate, stage_key, sn, "adjuster", "running")
        save(state, rstate)
        _refresh()
        p = _adjust_path(stage_key, sn, chapter, rnd)
        adj = _do_task(adjuster, _adjust_prompt(stage_key, sn, material, rev_text, dry, rnd),
                       p, log_fn, dry)
        if not (adj and adj.strip()):
            log_fn(f"    ✖ 修改稿（第{rnd}轮）为空，子步中断")
            cascade_fail_from_item(rstate, stage_key, sn, "adjuster")
            save(state, rstate)
            _refresh()
            return "", False
        if not _artifact_is_real(p):
            log_fn(f"    ⚠ 修改稿（第{rnd}轮）未生成真实文件，保持未通过（红）")
            save(state, rstate)
            _refresh()
            return "", False
        set_item_status(rstate, stage_key, sn, "adjuster", "pass")
        save(state, rstate)
        log_fn(f"    ✔ 修改通过（第{rnd}轮 / {adjuster}）")
        _plan_verify_pass(stage_key, sn, "adjuster", p, log_fn)
        _refresh()
        return adj, True

    if not reviewer:
        log_fn("    ⏭ 未指派可用的本地端审核者，跳过审核")
        return assembled or material

    rnd = loop_round(rstate, stage_key, sn)
    rev_text, ok = _run_review(rnd)
    if not ok:
        return ""
    if not adjuster:
        log_fn("    ⏭ 未指派可用的本地端调整者，跳过调整")
        return assembled or material
    adj_text, ok2 = _run_adjust(rnd, rev_text)
    if not ok2:
        return ""

    # 3) 环节终审闭环：审核未达标（打钩清单未全过，或数字评分未达门槛）→ 开启下一轮
    #    （审核复审 → 调整者再改）。规划复核等启用了 score_gate 的子步以分数为准。
    while is_stage_final and rnd < FINAL_LOOP_MAX_ROUNDS:
        _rtext = _read(_review_path(stage_key, sn, chapter, rnd))
        if _gate_passed(_rtext, gate):
            if gate is not None and not review_all_checked(_rtext):
                log_fn(f"    ✅ 第{rnd}轮审核综合评分达标（≥{gate}），调整者可交付")
            else:
                log_fn(f"    ✅ 第{rnd}轮审核已全部打钩，调整者可交付")
            break
        rnd += 1
        set_loop_round(rstate, stage_key, sn, rnd)
        set_item_status(rstate, stage_key, sn, "reviewer", "none")
        set_item_status(rstate, stage_key, sn, "adjuster", "none")
        save(state, rstate)
        _refresh()
        log_fn(f"    🔁 第 {rnd} 轮复检：审核未达标（分数未达门槛/仍有未打钩项）→ 审核复审 → 调整者再改")
        rev_text, ok = _run_review(rnd)
        if not ok:
            return ""
        adj_text, ok2 = _run_adjust(rnd, rev_text)
        if not ok2:
            return ""

    if is_stage_final and not _gate_passed(_read(_review_path(stage_key, sn, chapter, rnd)), gate):
        if gate is not None:
            log_fn(f"    ⚠ 已达最大复检轮次（{FINAL_LOOP_MAX_ROUNDS}），综合评分仍未达门槛（≥{gate}），"
                   f"请人工确认后再放行")
        else:
            log_fn(f"    ⚠ 已达最大复检轮次（{FINAL_LOOP_MAX_ROUNDS}），审核仍未全部打钩，请人工确认后再放行")
    return adj_text or (assembled or material)


# ----------------------------------------------------------------- 手动重发单个任务

def _assemble_step_material(stage_key, step_name, state):
    """读取某子步下所有已产出块的产物，拼成审核/修改的 material。"""
    outs = []
    blocks = state[stage_key]["steps"][step_name]["blocks"]
    for block, ai in blocks.items():
        if not ai:
            continue
        path = _produce_path(stage_key, step_name, block)
        txt = _read(path)
        if not txt:
            continue
        outs.append(f"# {block}（由 {ai} 产出）\n{txt}")
    return "\n\n".join(outs)


def resend_task(stage_key, step_name, task_type, task_key,
                log_fn=print, dry=None, timeout=600):
    """UI 上点「重发」时调用：按当前指派和最新产物，重新把任务发给对应 AI。

    task_type: 'block' | 'reviewer' | 'adjuster'
    task_key:  block 名称（block 类型）或角色名（reviewer/adjuster 类型，目前无意义）
    """
    if dry is None:
        dry = DRY_RUN
    state, _ = load()
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st:
        log_fn(f"❌ 未知环节: {stage_key}")
        return
    step = next((s for s in st["steps"] if s["name"] == step_name), None)
    if not step:
        log_fn(f"❌ 未知子步: {step_name}")
        return
    final = bool(step.get("final"))
    upstream = _upstream_text(stage_key)

    if task_type == "block":
        block = task_key
        ai = state[stage_key]["steps"][step_name]["blocks"].get(block)
        if not ai:
            log_fn(f"⚠ 块「{block}」未指派 AI，无法重发")
            return
        text = _block_prompt(stage_key, step_name, block, upstream, dry)
        out_path = _produce_path(stage_key, step_name, block)
        log_fn(f"🔄 重发块「{block}」→ {ai}")
        _do_task(ai, text, out_path, log_fn, dry, timeout)

    elif task_type == "reviewer":
        ai = state[stage_key]["steps"][step_name].get("reviewer")
        if not ai:
            log_fn(f"⚠ 子步「{step_name}」未指派审核者，无法重发")
            return
        material = _assemble_step_material(stage_key, step_name, state) or upstream
        text = _review_prompt(stage_key, step_name, material)
        out_path = _review_path(stage_key, step_name)
        log_fn(f"🔄 重发{'终审' if final else '审核'}→ {ai}")
        _do_task(ai, text, out_path, log_fn, dry, timeout)

    elif task_type == "adjuster":
        ai = state[stage_key]["steps"][step_name].get("adjuster")
        reviewer = state[stage_key]["steps"][step_name].get("reviewer")
        if not ai:
            log_fn(f"⚠ 子步「{step_name}」未指派调整者，无法重发")
            return
        material = _assemble_step_material(stage_key, step_name, state) or upstream
        review_path = _review_path(stage_key, step_name) if reviewer else None
        if not review_path or not os.path.exists(review_path):
            log_fn(f"⚠ 调整者重发需要先有审核意见（{reviewer or '未指派'} 的评审尚未生成）")
            return
        review_text = _read(review_path)
        text = _adjust_prompt(stage_key, step_name, material, review_text, dry)
        out_path = _adjust_path(stage_key, step_name)
        log_fn(f"🔄 重发修改→ {ai}")
        _do_task(ai, text, out_path, log_fn, dry, timeout)

    else:
        log_fn(f"❌ 未知任务类型: {task_type}")


# ----------------------------------------------------------------- 手动：逐块发送下一个子项
def _ordered_items(stage_key):
    """返回该大环节所有子项的顺序列表：[(step_name, item_type, item_key), ...]。

    item_type: 'block' | 'reviewer' | 'adjuster'；item_key 对块是块名，对审核/调整是字面量
    'reviewer' / 'adjuster'（与 item_status 的键保持一致）。
    """
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st:
        return []
    items = []
    for step in st["steps"]:
        sn = step["name"]
        for b in (step.get("blocks") or {}):
            items.append((sn, "block", b))
        if step.get("reviewer"):
            items.append((sn, "reviewer", "reviewer"))
        if step.get("adjuster"):
            items.append((sn, "adjuster", "adjuster"))
    return items


def _finalize_item(stage_key, sn, item, out, out_path, log_fn, rstate, state, refresh_fn, label):
    """发送后判定：空 / 非真实产物 → 级联失败并返回 False；否则标记通过返回 True。"""
    def _refresh():
        if refresh_fn:
            refresh_fn()
    if not (out and out.strip()):
        log_fn(f"    ✖ {label}产出为空，标记不通过")
        cascade_fail_from_item(rstate, stage_key, sn, item)
        save(state, rstate)
        _refresh()
        return False
    if not _artifact_is_real(out_path):
        log_fn(f"    ⚠ {label}未生成真实文件，保持未通过（红）")
        save(state, rstate)
        _refresh()
        return False
    plan_path = _plan_file_for(stage_key, sn)
    if plan_path:
        log_fn(f"    📋 已对照规划校验：{os.path.basename(out_path)}")
        if item != "reviewer" and not _plan_lists_output(plan_path, out_path):
            log_fn(f"    ⚠ 规划未列出此产出（规划漂移？请核对）：{os.path.basename(out_path)}")
    set_item_status(rstate, stage_key, sn, item, "pass")
    save(state, rstate)
    log_fn(f"    ✔ {label}通过（已读取真实文件）")
    _refresh()
    return True


def run_next_item(stage_key, log_fn=print, dry=True, refresh_fn=None, chapter=None):
    """手动模式：只运行本环节中【下一个】尚未通过的子项（块 / 审核 / 调整）。

    上下文 = 上一环节累积稿 + 本环节此前已通过子项的产物（按顺序累加），
    保证后续子项天然综合参考前面子项的产出；且严格等前一项完成才发下一项。
    返回 True 表示已发送并跑完一项；False 表示无待运行项（已全部通过）或前序未通过。
    """
    start_run()
    state, rstate = load()
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st:
        log_fn(f"❌ 未知环节: {stage_key}")
        return False
    items = _ordered_items(stage_key)
    if not items:
        return False

    def _refresh():
        if refresh_fn:
            refresh_fn()

    # 环节终审闭环：最后一个子步的审核/调整都已通过，但审核仍未全部打钩 → 开启下一轮复检
    lsn = last_step_name(stage_key)
    if lsn:
        rnd0 = loop_round(rstate, stage_key, lsn)
        rev_p = _review_path(stage_key, lsn, chapter, rnd0)
        adj_p = _adjust_path(stage_key, lsn, chapter, rnd0)
        both_done = (rstate["stages"][stage_key].get("item_status", {})
                     .get(lsn, {}).get("reviewer") == "pass"
                     and rstate["stages"][stage_key].get("item_status", {})
                     .get(lsn, {}).get("adjuster") == "pass")
        if (both_done and os.path.exists(rev_p) and os.path.exists(adj_p)
                and not review_all_checked(_read(rev_p))):
            if rnd0 < FINAL_LOOP_MAX_ROUNDS:
                rnd0 += 1
                set_loop_round(rstate, stage_key, lsn, rnd0)
                set_item_status(rstate, stage_key, lsn, "reviewer", "none")
                set_item_status(rstate, stage_key, lsn, "adjuster", "none")
                save(state, rstate)
                _refresh()
                log_fn(f"🔁 审核仍有未打钩项 → 开启第 {rnd0} 轮复检（审核复审 → 调整者再改）")
            else:
                log_fn(f"⚠ 已达最大复检轮次（{FINAL_LOOP_MAX_ROUNDS}），"
                       f"审核仍未全部打钩；请人工确认后放行或重发审核。")

    # 找到下一个未通过子项
    target = None
    for i, (sn, t, k) in enumerate(items):
        stt = (rstate["stages"][stage_key].get("item_status", {})
               .get(sn, {}).get(k, "none"))
        if stt != "pass":
            target = i
            break
    if target is None:
        log_fn("✅ 本环节所有子项均已通过，无需再发送；请点【放行】进入下一环节。")
        return False
    # 校验前序都已通过（避免跳跃发送导致上下文错乱）
    for i2 in range(target):
        sn, t, k = items[i2]
        if (rstate["stages"][stage_key].get("item_status", {})
                .get(sn, {}).get(k, "none") != "pass"):
            log_fn(f"⛔ 子项「{k}」之前还有未通过的子项，请按顺序先完成前面的子项。")
            return False

    # 构造上下文：上一环节累积稿 + 本环节已通过子项产物
    base = _upstream_text(stage_key)
    if chapter is not None and stage_key in CHAPTER_AWARE_STAGES:
        base = _chapter_upstream(stage_key, int(chapter), base)
    context = base
    for i2 in range(target):
        sn, t, k = items[i2]
        # 复检轮次的产物带 _第N轮 后缀，按该子步当前轮次取最新一份
        rr = loop_round(rstate, stage_key, sn) if k in ("reviewer", "adjuster") else 1
        p = _item_artifact_path(stage_key, sn, k, chapter, rr)
        txt = _read(p) if (p and os.path.exists(p)) else ""
        if not (txt and txt.strip()) and rr > 1:
            p0 = _item_artifact_path(stage_key, sn, k, chapter, 1)
            txt = _read(p0) if (p0 and os.path.exists(p0)) else ""
        if txt and txt.strip():
            context = (context + "\n\n" + f"# {k}\n{txt}") if context else f"# {k}\n{txt}"

    sn, t, k = items[target]
    rnd = loop_round(rstate, stage_key, sn)
    if t == "block":
        ai = state[stage_key]["steps"][sn]["blocks"].get(k)
        if not ai:
            log_fn(f"⛔ 块「{k}」未指派 AI，请先指派后再发送。")
            return False
        set_item_status(rstate, stage_key, sn, k, "running")
        save(state, rstate); _refresh()
        log_fn(f"  ▶ 手动发送块「{k}」→ {ai}")
        text = _block_prompt(stage_key, sn, k, context, dry)
        out = _do_task(ai, text, _produce_path(stage_key, sn, k, chapter), log_fn, dry)
        return _finalize_item(stage_key, sn, k, out,
                              _produce_path(stage_key, sn, k, chapter),
                              log_fn, rstate, state, refresh_fn, f"块「{k}」")

    if t == "reviewer":
        ai = local_role_guard(state[stage_key]["steps"][sn].get("reviewer"), "reviewer", log_fn)
        if not ai:
            log_fn(f"⛔ 子步「{sn}」无可用本地端审核者，无法发送。")
            return False
        # 环节终审：最后一个子步审核本环节全部产出（整合总结 + 打钩清单）
        material = context
        if sn == lsn:
            sm = assemble_stage_material(stage_key, state, chapter)
            if sm.strip():
                material = sm
                log_fn(f"  🧩 环节终审：已整合本环节全部产出（{len(sm)} 字符）")
        set_item_status(rstate, stage_key, sn, k, "running")
        save(state, rstate); _refresh()
        log_fn(f"  ▶ 手动发送审核（第{rnd}轮）→ {ai}")
        p = _review_path(stage_key, sn, chapter, rnd)
        text = _review_prompt(stage_key, sn, material, rnd)
        out = _do_task(ai, text, p, log_fn, dry)
        return _finalize_item(stage_key, sn, k, out, p,
                              log_fn, rstate, state, refresh_fn, f"审核「{sn}」")

    if t == "adjuster":
        ai = local_role_guard(state[stage_key]["steps"][sn].get("adjuster"), "adjuster", log_fn)
        if not ai:
            log_fn(f"⛔ 子步「{sn}」无可用本地端调整者，无法发送。")
            return False
        material = context
        if sn == lsn:
            sm = assemble_stage_material(stage_key, state, chapter)
            if sm.strip():
                material = sm
        rev_path = _review_path(stage_key, sn, chapter, rnd)
        rev = _read(rev_path) if os.path.exists(rev_path) else ""
        set_item_status(rstate, stage_key, sn, k, "running")
        save(state, rstate); _refresh()
        log_fn(f"  ▶ 手动发送调整（第{rnd}轮）→ {ai}")
        p = _adjust_path(stage_key, sn, chapter, rnd)
        text = _adjust_prompt(stage_key, sn, material, rev, dry, rnd)
        out = _do_task(ai, text, p, log_fn, dry)
        return _finalize_item(stage_key, sn, k, out, p,
                              log_fn, rstate, state, refresh_fn, f"调整「{sn}」")

    return False


# ----------------------------------------------------------------- 单大环节
def run_stage(stage_key, log_fn=print, dry=True, refresh_fn=None, chapter=None):
    """运行一个大环节的全部细化子步（自动连续）。全部通过后需用户手动放行。

    chapter 参数：
      · None（默认）→ 全本模式（兼容老链路）；
      · 整数      → 章为核心：只跑该章（写作/去AI/审核/出厂 每章一个完整流程）。
    """
    start_run()  # 每次运行先重置 停止/暂停 标志，避免上一次停止后重跑被立刻中断
    state, rstate = load()
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if not st:
        log_fn(f"❌ 未知环节: {stage_key}")
        return False
    rstate["stages"][stage_key]["status"] = "running"
    rstate["current_stage"] = stage_key
    save(state, rstate)
    if refresh_fn:
        refresh_fn()

    # 重跑前先清掉上次遗留在该环节的 fail 标记，避免旧失败态直接中止本次运行
    cleared = _clear_stage_stale_fails(stage_key, rstate)
    if cleared:
        log_fn(f"  ♻ 已清除本环节上次遗留的 {cleared} 个失败标记，本次运行重新判定")

    # 启动前按磁盘真实产物复核本环节状态：默认红，只有读取到真实文件才转绿
    _verify_stage_from_disk(stage_key, state, rstate, chapter)
    save(state, rstate)
    if refresh_fn:
        refresh_fn()

    upstream = _upstream_text(stage_key)
    if chapter is not None and stage_key in CHAPTER_AWARE_STAGES:
        log_fn(f"=== 环节【{stage_key}】第{int(chapter):03d}章 / 共{_chapter_count()}章 开始（dry={dry}）===")
    else:
        log_fn(f"=== 环节【{stage_key}】开始（dry={dry}）===")
    # 本步骤规划（AI 生成，落盘到 _logs 操作文件树）；无指派 AI 时跳过
    planner_ai = _pick_stage_ai(state, stage_key)
    step_dir = _logs_stage_dir(stage_key)
    _mkdir(step_dir)
    if planner_ai and not (_STOP or _PAUSE):
        log_fn(f"  📝 生成【本步骤规划】→ {planner_ai}")
        plan_path = os.path.join(step_dir, "本步骤规划.md")
        if chapter is not None and stage_key in CHAPTER_AWARE_STAGES:
            plan_path = os.path.join(step_dir, f"第{int(chapter):03d}章_本步骤规划.md")
        _do_task(planner_ai, _step_plan_prompt(stage_key, state), plan_path, log_fn, dry)
    parts = []
    N = _chapter_count()
    chapter_aware = stage_key in CHAPTER_AWARE_STAGES
    if chapter is not None and chapter_aware:
        # ---------- 章为核心：只跑「本章」（本章每个子步都带章号，先读上一章再生成）
        ch = int(chapter)
        chap_base = _chapter_upstream(stage_key, ch, upstream)
        log_fn(f"  📖 本章【第{ch:03d}章 / 共{N}章】：注入上一章（同环节）+ 上一环节同章内容")
        cur = chap_base
        for step in st["steps"]:
            if _STOP or _PAUSE:
                log_fn("⏸ 运行中收到停止/暂停信号，中断后续子步")
                break
            txt = _run_step(stage_key, step, state, rstate, cur, log_fn, dry,
                           refresh_fn, chapter=ch)
            if stage_failed_steps(rstate, stage_key):
                log_fn(f"=== 环节【{stage_key}】第{ch:03d}章生成失败，子步暂停，请修正后重跑 ===")
                save(state, rstate)
                if refresh_fn:
                    refresh_fn()
                return False
            parts.append(txt)
            cur = (cur + "\n\n" + txt) if txt else cur
    else:
        # ---------- 全本模式（chapter=None，兼容老链路 / run_all 全本）
        per_chapter_steps = set(PER_CHAPTER_STEPS.get(stage_key, []))
        chapter_mode = chapter_aware and N >= 1
        for step in st["steps"]:
            if _STOP or _PAUSE:
                log_fn("⏸ 运行中收到停止/暂停信号，中断后续子步")
                break
            # 按章循环的子步：每章先读上一章内容，再生成本章
            if chapter_mode and step["name"] in per_chapter_steps:
                for ch in range(1, N + 1):
                    if _STOP or _PAUSE:
                        break
                    chap_up = _chapter_upstream(stage_key, ch, upstream)
                    log_fn(f"  📖 第{ch:03d}章 / 共{N}章：子步[{step['name']}]")
                    txt = _run_step(stage_key, step, state, rstate, chap_up, log_fn, dry,
                                   refresh_fn, chapter=ch)
                    if stage_failed_steps(rstate, stage_key):
                        log_fn(f"=== 环节【{stage_key}】第{ch:03d}章生成失败，子步暂停，请修正后重跑 ===")
                        save(state, rstate)
                        if refresh_fn:
                            refresh_fn()
                        return False
                    parts.append(txt)
                    upstream = (upstream + "\n\n" + txt) if txt else upstream
            else:
                txt = _run_step(stage_key, step, state, rstate, upstream, log_fn, dry, refresh_fn)
                if stage_failed_steps(rstate, stage_key):
                    log_fn(f"=== 环节【{stage_key}】因子步失败暂停，请修正后重跑 ===")
                    save(state, rstate)
                    if refresh_fn:
                        refresh_fn()
                    return False
                parts.append(txt)
                upstream = (upstream + "\n\n" + txt) if txt else upstream
    # 写环节产出索引（供下一环节注入）：只列文件路径，不再内联全文，避免重复存储
    _write(_context_path(stage_key), _build_context_index(stage_key, state))
    save(state, rstate)
    if refresh_fn:
        refresh_fn()

    # 下一步建议（AI 生成，落盘到环节目录）
    if planner_ai and not (_STOP or _PAUSE):
        log_fn(f"  📝 生成【下一步建议】→ {planner_ai}")
        advice_path = os.path.join(step_dir, "下一步建议.md")
        if chapter is not None and stage_key in CHAPTER_AWARE_STAGES:
            advice_path = os.path.join(step_dir, f"第{int(chapter):03d}章_下一步建议.md")
        _do_task(planner_ai, _next_step_advice_prompt(stage_key, state), advice_path, log_fn, dry)

    if stage_all_passed(rstate, stage_key):
        log_fn(f"=== 环节【{stage_key}】全部通过，请核对后点击【放行】进入下一环节 ===")
        return True
    else:
        log_fn(f"=== 环节【{stage_key}】细化子步完成；尚有未通过项，请检查指派与执行结果 ===")
        return False


# ----------------------------------------------------------------- 全自动（章为核心：每章完整跑完 5 环节再放行，自动进入下一章）
def run_all(log_fn=print, dry=True, start_chapter=1, chapter_count=None, refresh_fn=None):
    """全自动串跑：每章按 写作→去AI→审核→出厂 跑完并自动放行，再进下一章。

    chapter_count: 要连续跑多少章；None 表示从 start_chapter 起跑完全部章节。
    refresh_fn: 运行完一个阶段或自动放行后回调，用于 UI 刷新。
    """
    _reset_stop()
    state, rstate = load()
    total = _chapter_count()
    start = max(1, int(start_chapter) if start_chapter is not None else 1)
    end = total
    if chapter_count is not None:
        end = min(start + int(chapter_count) - 1, total)
    need = end - start + 1          # 有几章就要跑几个循环（每章 = 环节2→3→4→5 一轮）
    done_cycles = 0
    stopped = False
    log_fn(f"🚀 程序二全自动开始（dry={dry}，第{start:03d}章→第{end:03d}章 / 共{total}章，需完成 {need} 轮循环）")
    for ch in range(start, end + 1):
        if _STOP or _PAUSE:
            log_fn("⏸ 全自动中断（暂停/停止）")
            break
        reset_chapter_cycle()           # 每章重置章核心环节门控
        set_current_chapter(ch)
        save_chapter_progress()
        log_fn(f"📖 第{ch:03d}章 / 共{total}章（第{done_cycles + 1}/{need}轮循环）")
        gate_failed = False
        for sk in CHAPTER_AWARE_STAGES:
            if _STOP or _PAUSE:
                break
            try:
                run_stage(sk, log_fn, dry, refresh_fn=refresh_fn, chapter=ch)
            except Exception as _e:
                import traceback as _tb
                log_fn("❌ 环节【%s】第%03d章执行异常：" % (sk, ch))
                for _ln in _tb.format_exception(type(_e), _e, _e.__traceback__):
                    log_fn("   " + _ln.rstrip())
                log_fn("⏭ 跳过本环节，继续后续环节/章节")
                continue
            if _STOP or _PAUSE:
                log_fn("⏸ 全自动已暂停/停止，终止后续章节与放行")
                break
            try:
                state, rstate = load()   # 重新载入，避免覆盖 run_stage 刚写入的子项状态
                if not stage_all_passed(rstate, sk):
                    # 环节尚有未通过项：不再自动放行，避免把失败/缺产物环节推进下游造成级联污染
                    log_fn(f"  ⛔ 环节【{sk}】(第{ch:03d}章) 尚有未通过项，自动放行中止，请修正后手动处理")
                    gate_failed = True
                    break
                user_passes_gate(rstate, sk)
                save(state, rstate)
                log_fn(f"  ✅ 自动放行 {sk}（第{ch:03d}章）")
                if refresh_fn:
                    refresh_fn()
            except Exception as _e2:
                import traceback as _tb2
                log_fn("❌ 自动放行【%s】第%03d章异常：" % (sk, ch))
                for _ln in _tb2.format_exception(type(_e2), _e2, _e2.__traceback__):
                    log_fn("   " + _ln.rstrip())
        if gate_failed:
            stopped = True
            log_fn("⏸ 因环节未全部通过，全自动已中止，请检查后重跑本环节")
            break
        # ---- 本轮（该章）是否按 环节2→3→4→5 跑完一轮完整循环 ----
        if _STOP or _PAUSE:
            stopped = True
            log_fn("⏸ 检测到停止/暂停信号，终止后续循环")
            break
        done_cycles += 1
        log_fn(f"  🔁 第{done_cycles}/{need}轮循环完成：第{ch:03d}章已在【环节5 出厂】收尾")
        if done_cycles >= need:
            log_fn(f"  ✔ 循环次数校验通过：已按要求完成 {done_cycles}/{need} 轮")

    # ---- 跑完要求循环后：停在【环节2 写作】，是否开启下一轮由用户决定 ----
    if not stopped:
        try:
            nxt = end + 1
            if nxt <= total:
                set_current_chapter(nxt)
                save_chapter_progress()
                reset_chapter_cycle()   # 内部会把 current_stage 置为「写作」
                log_fn(f"⏭ 已就绪第{nxt:03d}章，界面停在【环节2 写作】")
            else:
                state, rstate = load()
                rstate["current_stage"] = CHAPTER_AWARE_STAGES[0]   # 停在环节2 写作
                save(state, rstate)
                log_fn(f"🏁 第{start:03d}章→第{end:03d}章已全部跑完（{done_cycles}/{need} 轮），界面停在【环节2 写作】")
            if refresh_fn:
                refresh_fn()
        except Exception as _e3:
            log_fn(f"⚠ 收尾回到环节2失败：{_e3}")
        log_fn("⏸ 已停在【环节2 写作】界面：点「▶ 执行本环节」继续本轮，或点「🚀 全自动串跑」开启下一轮循环")
    log_fn("🎉 全自动串跑结束")


# ----------------------------------------------------------------- 线程封装
def run_all_threaded(log_fn=print, dry=True, done_fn=None, start_chapter=1,
                     chapter_count=None, refresh_fn=None):
    def _t():
        try:
            run_all(log_fn, dry, start_chapter, chapter_count, refresh_fn)
        finally:
            if done_fn:
                done_fn()
    th = threading.Thread(target=_t, daemon=True)
    th.start()
    return th


if __name__ == "__main__":
    # 自测：dry 跑一遍全链路，验证门控与产物落盘
    set_dry_run(True)
    import stage_board as sb
    s, r = sb.load()
    sb.assign_block(s, "规划", "规划产出", "人物系统", "deepseek")
    sb.assign_role(s, "规划", "规划产出", "reviewer", "gemini")
    sb.assign_role(s, "规划", "规划产出", "adjuster", "tongyi")
    sb.assign_block(s, "写作", "章纲", "章纲产出", "kimi")
    sb.assign_role(s, "写作", "章纲", "reviewer", "deepseek")
    sb.assign_block(s, "写作", "正文", "正文产出", "doubao")
    sb.assign_role(s, "写作", "正文", "reviewer", "gemini")
    sb.save(s, r)

    run_all(print, dry=True)
    print("== 环节上下文文件 ==")
    for sk in STAGE_ORDER:
        p = _context_path(sk)
        print(f"  {sk}: {'OK' if os.path.exists(p) else '缺失'}")
    print("== auto_stage 自测完成（接入 mix_send.send =",
          _mix_send.__module__ == "mix_send", "）==")
