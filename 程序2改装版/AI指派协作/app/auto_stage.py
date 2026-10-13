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


def _block_file(stage_key, step_name, block):
    st = next(s for s in PIPELINE if s["key"] == stage_key)
    step = next(s for s in st["steps"] if s["name"] == step_name)
    idx = step["blocks"].index(block) + 1
    return f"{STAGE_ORDER.index(stage_key)+1}-{idx}_{block}.md"


def _use_folder_layout(stage_key):
    """规划大环节保持原平铺结构；其余大环节按「子步名」分文件夹存放。"""
    return stage_key != "规划"


def _produce_path(stage_key, step_name, block, chapter=None):
    name = _block_file(stage_key, step_name, block)
    if chapter and chapter >= 1:
        name = f"第{chapter:03d}章_{block}.md"
    if _use_folder_layout(stage_key):
        # 块产出按子步名单独建文件夹：正文→正文/ 、章纲→章纲/ …
        return os.path.join(_stage_dir(stage_key), step_name, name)
    return os.path.join(_stage_dir(stage_key), name)


def _review_path(stage_key, step_name, chapter=None):
    name = f"{step_name}_审核意见.md"
    if chapter and chapter >= 1:
        name = f"第{chapter:03d}章_{step_name}_审核意见.md"
    if _use_folder_layout(stage_key):
        # 审核意见按「子步名+审核意见」单独建文件夹
        return os.path.join(_stage_dir(stage_key), f"{step_name}审核意见", name)
    return os.path.join(_stage_dir(stage_key), name)


def _adjust_path(stage_key, step_name, chapter=None):
    name = f"{step_name}_调整稿.md"
    if chapter and chapter >= 1:
        name = f"第{chapter:03d}章_{step_name}_调整稿.md"
    if _use_folder_layout(stage_key):
        # 调整稿按「子步名+调整稿」单独建文件夹
        return os.path.join(_stage_dir(stage_key), f"{step_name}调整稿", name)
    return os.path.join(_stage_dir(stage_key), name)


def _context_path(stage_key):
    return os.path.join(_stage_dir(stage_key), "_context.md")


# ----------------------------------------------------------------- 真实产物校验（默认红，只有读取到真实文件才转绿）
# MOCK 模式下只验证文件已落盘且非空，方便流程测试时方块正常变绿；
# 真实模式下要求内容不少于 20 字节，避免被占位/空内容糊弄。
_REAL_MIN_BYTES = 1 if MOCK_PROMPTS else 20


def _item_artifact_path(stage_key, step_name, item, chapter):
    """返回某子项（块 / 审核者 / 调整者）对应的产物文件路径。"""
    st = next((s for s in PIPELINE if s["key"] == stage_key), None)
    if st is None:
        return None
    step = next((s for s in st["steps"] if s["name"] == step_name), None)
    if step is None:
        return None
    if item == "reviewer":
        return _review_path(stage_key, step_name, chapter)
    if item == "adjuster":
        return _adjust_path(stage_key, step_name, chapter)
    if item in step.get("blocks", {}):
        return _produce_path(stage_key, step_name, item, chapter)
    return None


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
    """子步下的全部子项名（块 + reviewer/adjuster；终审子步只有 reviewer）。"""
    items = list(step.get("blocks", []) or [])
    if step.get("final"):
        items.append("reviewer")
    else:
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
            parts.append(f"# 上游环节【{sk}】已产出内容\n" + _read(c))
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
def _prompt_template_path(stage_key, step_name, task_type, task_key=None):
    folder_idx = STAGE_ORDER.index(stage_key) + 1
    folder = f"{folder_idx:02d}_{stage_key}"
    candidates = []
    if task_type == "block" and task_key:
        candidates.append(_block_file(stage_key, step_name, task_key))
    elif task_type == "reviewer":
        candidates.append("_审核者.md")
    elif task_type == "adjuster":
        candidates.append("_调整者.md")
    for c in candidates:
        p = paths.prompt_path(folder, c)
        if os.path.exists(p):
            return p
    return None


def _load_prompt_template(stage_key, step_name, task_type, task_key=None):
    p = _prompt_template_path(stage_key, step_name, task_type, task_key)
    return _read(p) if p else None


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


def _review_prompt(stage_key, step_name, material):
    template = _load_prompt_template(stage_key, step_name, "reviewer")
    if template:
        return _fill_prompt(template, material=material)
    return build_review_prompt(stage_key, step_name, "作品", material)


def _adjust_prompt(stage_key, step_name, material, review, dry):
    template = _load_prompt_template(stage_key, step_name, "adjuster")
    if template:
        return _fill_prompt(template, material=material, review=review)
    head = ("【修改任务】下面是一份待修改稿与对应的评审意见。"
            "请严格按评审意见逐条修改完善，输出修改后的【完整稿】（不要只给 diff）。\n")
    body = (f"\n=== 待修改稿 ===\n{material}\n\n=== 评审意见 ===\n{review}\n")
    return head + body


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


def _do_task(ai, text, out_path, log_fn, dry, timeout=600):
    """发送一个任务给 ai，并取回其写盘产物。dry 模式直接落占位。

    真实模式：调用 windows-use/mix_send.send(ai, directive) 把任务投到对应 AI 窗口，
    AI 按要求把结果写入 out_path，本函数轮询该文件作为回执。
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

    def _find_artifact():
        # 精确路径优先；模拟模式下 AI 可能把产物写进块同名子目录，也一并接受
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

    def _accept(art):
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
        log_fn(f"    ✅ 已收到 {os.path.basename(out_path)}（{sz} 字节），确认通过，进入下一项")
        return _read(out_path)

    art = _find_artifact()
    if not dry and art is not None:
        log_fn(f"    ↺ {ai} 已有产物，跳过（{os.path.basename(out_path)}）")
        return _accept(art)
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
    try:
        r = _mix_send(ai, directive)
    except Exception as e:
        log_fn(f"    ❌ {ai} 发送失败: {e}")
        return ""
    # 发送返回的是字符串；CDP/pyautogui 失败时返回带 ⚠/失败 的说明而非抛异常，
    # 此时不应再傻等文件（AI 根本没收到），直接判该块失败，让环节尽快结束给出明确反馈
    ok_send = bool(r) and (str(r).lstrip().startswith("✅")
                           or "已发送" in str(r)
                           or str(r).strip().lower().startswith("ok")
                           or "pyautogui ok" in str(r))
    if not ok_send:
        log_fn(f"    ❌ {ai} 发送未成功（{r}），跳过等待并标记该块失败")
        return ""
    log_fn(f"    → {ai}: 已发送任务（{r}）")
    if ai_is_web:
        # 网页端：从页面抓取回复并保存，不再等写盘
        return _capture_and_save(ai, out_path, log_fn, timeout)
    # 本地端：等待 AI 把结果写盘
    log_fn(f"    ⏳ 等待 {ai} 生成并写盘 {os.path.basename(out_path)}（确认收到后才进行下一项）…")
    t0 = time.time()
    while time.time() - t0 < timeout:
        if _STOP:
            log_fn(f"    ⏸ {ai} 收到停止信号")
            return _read(out_path) if os.path.exists(out_path) else ""
        art = _find_artifact()
        if art is not None:
            return _accept(art)
        time.sleep(5)
    # 超时收尾：模拟模式下若 AI 已建立目录结构（但无文本内容），仍放行但明确警告
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
    log_fn(f"    ⚠ {ai} 超时未写盘（{timeout}s），继续")
    return _read(out_path) if os.path.exists(out_path) else ""


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
        return _item_artifact_path(stage_key, sn, item, chapter)

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

    # 2) 审核 + 修改
    if final:
        if reviewer:
            if _halted():
                return ""
            done = _skip_if_done("reviewer")
            if done is None:
                set_item_status(rstate, stage_key, sn, "reviewer", "running")
                save(state, rstate)
                _refresh()
                rev = _do_task(reviewer, _review_prompt(stage_key, sn, material),
                               _review_path(stage_key, sn, chapter), log_fn, dry)
                if not (rev and rev.strip()):
                    log_fn(f"    ✖ 终审为空，不通过")
                    cascade_fail_from_item(rstate, stage_key, sn, "reviewer")
                    save(state, rstate)
                    _refresh()
                    return ""
                if not _artifact_is_real(_review_path(stage_key, sn, chapter)):
                    log_fn(f"    ⚠ 终审未生成真实文件，保持未通过（红）")
                    save(state, rstate)
                    _refresh()
                    return ""
                set_item_status(rstate, stage_key, sn, "reviewer", "pass")
                save(state, rstate)
                log_fn(f"    ✔ 终审通过（{reviewer}）")
                _plan_verify_pass(stage_key, sn, "reviewer", _review_path(stage_key, sn, chapter), log_fn)
            _refresh()
        return assembled or material

    if reviewer:
        if _halted():
            return ""
        done = _skip_if_done("reviewer")
        if done is not None:
            rev = done
        else:
            set_item_status(rstate, stage_key, sn, "reviewer", "running")
            save(state, rstate)
            _refresh()
            rev = _do_task(reviewer, _review_prompt(stage_key, sn, material),
                           _review_path(stage_key, sn, chapter), log_fn, dry)
            if not (rev and rev.strip()):
                log_fn(f"    ✖ 审核为空，子步中断")
                cascade_fail_from_item(rstate, stage_key, sn, "reviewer")
                save(state, rstate)
                _refresh()
                return ""
            if not _artifact_is_real(_review_path(stage_key, sn, chapter)):
                log_fn(f"    ⚠ 审核未生成真实文件，保持未通过（红）")
                save(state, rstate)
                _refresh()
                return ""
            set_item_status(rstate, stage_key, sn, "reviewer", "pass")
            save(state, rstate)
            log_fn(f"    ✔ 审核通过（{reviewer}）")
            _plan_verify_pass(stage_key, sn, "reviewer", _review_path(stage_key, sn, chapter), log_fn)
            _refresh()
        if adjuster:
            if _halted():
                return ""
            done2 = _skip_if_done("adjuster")
            if done2 is not None:
                adj = done2
            else:
                set_item_status(rstate, stage_key, sn, "adjuster", "running")
                save(state, rstate)
                _refresh()
                adj = _do_task(adjuster, _adjust_prompt(stage_key, sn, material, rev, dry),
                               _adjust_path(stage_key, sn, chapter), log_fn, dry)
                if not (adj and adj.strip()):
                    log_fn(f"    ✖ 修改稿为空，子步中断")
                    cascade_fail_from_item(rstate, stage_key, sn, "adjuster")
                    save(state, rstate)
                    _refresh()
                    return ""
                if not _artifact_is_real(_adjust_path(stage_key, sn, chapter)):
                    log_fn(f"    ⚠ 修改稿未生成真实文件，保持未通过（红）")
                    save(state, rstate)
                    _refresh()
                    return ""
                set_item_status(rstate, stage_key, sn, "adjuster", "pass")
                save(state, rstate)
                log_fn(f"    ✔ 修改通过（{adjuster}）")
                _plan_verify_pass(stage_key, sn, "adjuster", _adjust_path(stage_key, sn, chapter), log_fn)
            _refresh()
            return adj
    return assembled or material


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
        if (not step.get("final")) and step.get("adjuster"):
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
        p = _item_artifact_path(stage_key, sn, k, chapter)
        txt = _read(p) if (p and os.path.exists(p)) else ""
        if txt and txt.strip():
            context = (context + "\n\n" + f"# {k}\n{txt}") if context else f"# {k}\n{txt}"

    sn, t, k = items[target]
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
        ai = state[stage_key]["steps"][sn].get("reviewer")
        if not ai:
            log_fn(f"⛔ 子步「{sn}」未指派审核者，无法发送。")
            return False
        set_item_status(rstate, stage_key, sn, k, "running")
        save(state, rstate); _refresh()
        log_fn(f"  ▶ 手动发送审核 → {ai}")
        text = _review_prompt(stage_key, sn, context)
        out = _do_task(ai, text, _review_path(stage_key, sn, chapter), log_fn, dry)
        return _finalize_item(stage_key, sn, k, out,
                              _review_path(stage_key, sn, chapter),
                              log_fn, rstate, state, refresh_fn, f"审核「{sn}」")

    if t == "adjuster":
        ai = state[stage_key]["steps"][sn].get("adjuster")
        if not ai:
            log_fn(f"⛔ 子步「{sn}」未指派调整者，无法发送。")
            return False
        rev_path = _review_path(stage_key, sn, chapter)
        rev = _read(rev_path) if os.path.exists(rev_path) else ""
        set_item_status(rstate, stage_key, sn, k, "running")
        save(state, rstate); _refresh()
        log_fn(f"  ▶ 手动发送调整 → {ai}")
        text = _adjust_prompt(stage_key, sn, context, rev, dry)
        out = _do_task(ai, text, _adjust_path(stage_key, sn, chapter), log_fn, dry)
        return _finalize_item(stage_key, sn, k, out,
                              _adjust_path(stage_key, sn, chapter),
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
    # 本步骤规划（AI 生成，落盘到环节目录）；无指派 AI 时跳过
    planner_ai = _pick_stage_ai(state, stage_key)
    step_dir = _stage_dir(stage_key)
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
    # 写环节累积上下文（供下一环节注入）
    _write(_context_path(stage_key), "\n\n---\n\n".join(parts))
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
