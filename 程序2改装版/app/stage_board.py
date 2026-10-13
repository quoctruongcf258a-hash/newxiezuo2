"""stage_board.py
程序二·协同写作固定流水线数据模型 + 子步勾叉门控。
"""
import os
import json
import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导

ROOT = paths.APP_ROOT
COLLAB_ROOT = paths.APP_ROOT
DEFAULT_PATH = paths.join("work", "collab", "stage_board.json")


# ────────────────────────────────────────────────────────────
# 从 rings_items.json 动态生成 PIPELINE（33 环等）
# ────────────────────────────────────────────────────────────
_RING_STAGE_MAP = [
    ("01_规划", "规划", "对当前项目全部规划环做深度完善"),
    ("02_写作", "写作", "章纲 → 正文"),
    ("03_去AI", "去AI", "去 AI 味润色"),
    ("04_审核", "审核", "质检评审"),
    ("05_出厂", "出厂", "上架前低级错误检查"),
]


def _load_rings_items():
    p = paths.join("rules", "rings_items.json")
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _build_pipeline_from_rings():
    rings = _load_rings_items()
    if not rings:
        return None
    out = []
    for stage_key, label, desc in _RING_STAGE_MAP:
        info = rings.get(stage_key, {})
        items = info.get("环节", [])
        if not items:
            continue
        steps = []
        for item in items:
            name = item.get("name") or item.get("code") or "?"
            steps.append({
                "name": name,
                "code": item.get("code", name),
                "norms": False,
                "blocks": ["产出"],
                "mode": item.get("type", "mesh"),
                "desc": item.get("desc", ""),
            })
        out.append({
            "key": label,
            "label": label,
            "desc": desc,
            "steps": steps,
        })
    return out or None


DIMS = ["兼容", "结构", "衔接", "角色", "创意", "节奏", "文笔", "落地"]
EXTENDED_SCHEMA = {
    "兼容": ["设定自洽", "人设一致", "前文承接"],
    "结构": ["开篇钩子", "叙事推进", "详略配比"],
    "衔接": ["场景/时空连贯", "过渡自然"],
    "角色": ["动机合理", "声音辨识", "弧光/成长"],
    "创意": ["点子新颖", "意象质量", "反转力度"],
    "节奏": ["张弛控制", "信息密度"],
    "文笔": ["句式与修辞", "语感统一", "零硬伤"],
    "落地": ["可推进性", "指导性", "情绪落点"],
}
SUB_KEYS = [f"{d}·{s}" for d, subs in EXTENDED_SCHEMA.items() for s in subs]
NORMATIVE_SUBS = ["文笔·零硬伤", "文笔·句式与修辞"]

_RING_PIPELINE = _build_pipeline_from_rings()

PIPELINE = _RING_PIPELINE if _RING_PIPELINE else [
    {"key": "规划", "label": "规划", "desc": "（兜底）",
     "steps": [{"name": "规划复核", "norms": False, "blocks": ["产出"]}]},
    {"key": "写作", "label": "写作", "desc": "（兜底）",
     "steps": [{"name": "章纲", "norms": False, "blocks": ["产出"]},
               {"name": "正文", "norms": True, "blocks": ["产出"]}]},
    {"key": "去AI", "label": "去AI", "desc": "（兜底）",
     "steps": [{"name": "去AI润色", "norms": True, "blocks": ["产出"]}]},
    {"key": "审核", "label": "审核", "desc": "（兜底）",
     "steps": [{"name": "质检评审", "norms": True, "blocks": ["产出"]}]},
    {"key": "出厂", "label": "出厂", "desc": "（兜底）",
     "steps": [{"name": "出厂检查", "norms": True, "blocks": ["产出"]}]},
]

STAGE_ORDER = [s["key"] for s in PIPELINE]
ENFORCE_CROSS_VENDOR = False
STAGE_MANUAL_GATE = True


def auto_steps(stage_key):
    st = next(s for s in PIPELINE if s["key"] == stage_key)
    return [s["name"] for s in st["steps"]]


def _step_names(stage_key):
    st = next((x for x in PIPELINE if x["key"] == stage_key), None)
    if st is None:
        return []
    return [x["name"] for x in st["steps"]]


def _step_items(stage_key, step_name):
    st = next((x for x in PIPELINE if x["key"] == stage_key), None)
    if st is None:
        return []
    step = next((x for x in st["steps"] if x["name"] == step_name), None)
    if step is None:
        return []
    items = list(step.get("blocks", []))
    # 终审子步同样需要「调整者」：环节终审闭环要求 审核→调整→复审→全部打钩才交付，
    # 没有调整者就无法闭环。
    items.extend(["reviewer", "adjuster"])
    return items


def new_run_state():
    return {
        "current_stage": STAGE_ORDER[0],
        "stages": {
            sk: {
                "status": "pending",
                "current_step": None,
                "manual_gate": STAGE_MANUAL_GATE,
                "step_status": {n: "none" for n in _step_names(sk)},
                "item_status": {n: {it: "none" for it in _step_items(sk, n)}
                              for n in _step_names(sk)},
            }
            for sk in STAGE_ORDER
        },
    }

def set_step_status(run_state, stage_key, step_name, status):
    if status not in ("none", "pass", "fail"):
        raise ValueError("status must be none/pass/fail")
    st = run_state["stages"][stage_key]
    if "step_status" not in st:
        st["step_status"] = {n: "none" for n in _step_names(stage_key)}
    st["step_status"][step_name] = status
    # 同步到该子步下的所有 item
    for it in _step_items(stage_key, step_name):
        st.setdefault("item_status", {}).setdefault(step_name, {})[it] = status
    if status == "fail":
        names = _step_names(stage_key)
        if step_name in names:
            i = names.index(step_name)
            for n in names[i + 1:]:
                st["step_status"][n] = "fail"
                for it in _step_items(stage_key, n):
                    st.setdefault("item_status", {}).setdefault(n, {})[it] = "fail"
    return run_state


def set_item_status(run_state, stage_key, step_name, item, status):
    if status not in ("none", "pass", "fail", "running"):
        raise ValueError("status must be none/pass/fail/running")
    st = run_state["stages"][stage_key]
    st.setdefault("item_status", {}).setdefault(step_name, {})[item] = status
    # 任一子项 fail，该子步后续子项全部级联 fail
    if status == "fail":
        items = _step_items(stage_key, step_name)
        if item in items:
            i = items.index(item)
            for later in items[i + 1:]:
                st["item_status"][step_name][later] = "fail"
    # 推导 step_status
    items = _step_items(stage_key, step_name)
    vals = [st["item_status"][step_name].get(it, "none") for it in items]
    if all(v == "pass" for v in vals):
        st["step_status"][step_name] = "pass"
    elif any(v == "fail" for v in vals):
        st["step_status"][step_name] = "fail"
    else:
        st["step_status"][step_name] = "none"
    return run_state


def get_step_status(run_state, stage_key, step_name):
    st = run_state["stages"][stage_key]
    items = _step_items(stage_key, step_name)
    if not items:
        return st.get("step_status", {}).get(step_name, "none")
    vals = [st.get("item_status", {}).get(step_name, {}).get(it, "none") for it in items]
    if all(v == "pass" for v in vals):
        return "pass"
    if any(v == "fail" for v in vals):
        return "fail"
    return "none"


def cascade_fail_from(run_state, stage_key, step_name):
    """从指定子步起（含）向后跨大环节级联 fail，并把当前运行位置回退到该子步所在环节。"""
    seq = [(s["key"], st["name"]) for s in PIPELINE for st in s["steps"]]
    try:
        i = seq.index((stage_key, step_name))
    except ValueError:
        return run_state
    run_state["current_stage"] = stage_key
    for k, n in seq[i:]:
        run_state["stages"][k]["step_status"][n] = "fail"
        for it in _step_items(k, n):
            run_state["stages"][k].setdefault("item_status", {}).setdefault(n, {})[it] = "fail"
    idx = STAGE_ORDER.index(stage_key)
    run_state["stages"][stage_key]["status"] = "running"
    for later in STAGE_ORDER[idx + 1:]:
        run_state["stages"][later]["status"] = "pending"
    return run_state


def stage_all_passed(run_state, stage_key):
    names = _step_names(stage_key)
    return bool(names) and all(get_step_status(run_state, stage_key, n) == "pass" for n in names)


def previous_stages_passed(run_state, stage_key):
    idx = STAGE_ORDER.index(stage_key)
    return all(run_state["stages"][STAGE_ORDER[i]]["status"] == "passed" for i in range(idx))


def cascade_later_stages(run_state, stage_key):
    """指定大环节之后的所有大环节（含其下子步/子项）全部置 fail。"""
    idx = STAGE_ORDER.index(stage_key)
    run_state["current_stage"] = stage_key
    run_state["stages"][stage_key]["status"] = "running"
    for later in STAGE_ORDER[idx + 1:]:
        st = run_state["stages"][later]
        st["status"] = "pending"
        for n in _step_names(later):
            st["step_status"][n] = "fail"
            for it in _step_items(later, n):
                st["item_status"].setdefault(n, {})[it] = "fail"
    return run_state


def _all_items_seq():
    """整条流水线展平的 (stage, step, item) 序列，按显示顺序排列。"""
    seq = []
    for s in PIPELINE:
        for st in s["steps"]:
            for it in _step_items(s["key"], st["name"]):
                seq.append((s["key"], st["name"], it))
    return seq


def _item_index(stage_key, step_name, item):
    """返回指定子项在展平流水线中的下标；找不到则抛 ValueError。"""
    return _all_items_seq().index((stage_key, step_name, item))


def compute_frontier(run_state):
    """返回整条流水线中第一个非 pass 子项的下标；全部 pass 则返回序列长度。"""
    seq = _all_items_seq()
    for i, (sk, sn, it) in enumerate(seq):
        v = run_state["stages"][sk].get("item_status", {}).get(sn, {}).get(it, "none")
        if v != "pass":
            return i
    return len(seq)


def item_locked(run_state, stage_key, step_name, item):
    """该子项是否因处于流水线前沿之后而被锁定（不能通过）。"""
    try:
        idx = _item_index(stage_key, step_name, item)
    except ValueError:
        return True
    return idx > compute_frontier(run_state)


def stage_reachable(run_state, stage_key):
    """该大环节是否已解锁（是当前环节或前面所有大环节已放行）。"""
    if stage_key == run_state.get("current_stage"):
        return True
    idx = STAGE_ORDER.index(stage_key)
    return all(run_state["stages"][STAGE_ORDER[i]]["status"] == "passed" for i in range(idx))


def cascade_fail_from_item(run_state, stage_key, step_name, item):
    """从指定子项起（含）向后跨子步/跨大环节全部级联 fail。

    用于「前面任一子项不通过，后续全部自动变不通过」的门控语义：
    当前子项及其后的所有子项（含同子步后续项、同大环节后续子步、
    后续所有大环节）一律置 fail。
    """
    seq = _all_items_seq()
    try:
        i = seq.index((stage_key, step_name, item))
    except ValueError:
        return run_state
    run_state["current_stage"] = stage_key
    run_state["stages"][stage_key]["status"] = "running"
    # 当前子项本身也要置为不通过
    set_item_status(run_state, stage_key, step_name, item, "fail")
    for k, n, it in seq[i + 1:]:
        set_item_status(run_state, k, n, it, "fail")
    idx = STAGE_ORDER.index(stage_key)
    for later in STAGE_ORDER[idx + 1:]:
        run_state["stages"][later]["status"] = "pending"
    return run_state


def previous_items_failed(run_state, stage_key, step_name, item):
    """检查指定子项之前是否存在任何已 fail 的子项（跨子步/跨大环节）。"""
    seq = _all_items_seq()
    try:
        i = seq.index((stage_key, step_name, item))
    except ValueError:
        return False
    for k, n, it in seq[:i]:
        v = run_state["stages"][k].get("item_status", {}).get(n, {}).get(it, "none")
        if v == "fail":
            return True
    return False


def enforce_cascade(run_state):
    """强制整条流水线的级联语义：前面任一子项 fail，后面所有子项全部置 fail。

    用于启动时修复旧状态，以及外部脚本修正持久化数据。
    """
    seq = _all_items_seq()
    seen_fail = False
    fixed = 0
    for k, n, it in seq:
        v = run_state["stages"][k].get("item_status", {}).get(n, {}).get(it, "none")
        if v == "fail":
            seen_fail = True
        elif seen_fail:
            set_item_status(run_state, k, n, it, "fail")
            fixed += 1
    return fixed


def reset_later_stages(run_state, stage_key):
    """指定大环节之后的所有大环节（含其下子步/子项）重置为 none。"""
    idx = STAGE_ORDER.index(stage_key)
    for later in STAGE_ORDER[idx + 1:]:
        st = run_state["stages"][later]
        st["status"] = "pending"
        for n in _step_names(later):
            st["step_status"][n] = "none"
            for it in _step_items(later, n):
                st["item_status"].setdefault(n, {})[it] = "none"
    return run_state


def stage_failed_steps(run_state, stage_key):
    st = run_state["stages"][stage_key]
    ss = st.get("step_status") or {}
    return [n for n, v in ss.items() if v == "fail"]


def user_passes_gate(run_state, stage_key=None):
    sk = stage_key or run_state["current_stage"]
    if sk not in STAGE_ORDER:
        raise KeyError(f"未知环节: {sk}")
    idx = STAGE_ORDER.index(sk)
    run_state["stages"][sk]["status"] = "passed"
    if idx + 1 < len(STAGE_ORDER):
        nxt = STAGE_ORDER[idx + 1]
        run_state["stages"][nxt]["status"] = "running"
        run_state["current_stage"] = nxt
    else:
        run_state["current_stage"] = sk
    return run_state


def gate_status(run_state, stage_key=None):
    sk = stage_key or run_state["current_stage"]
    return run_state["stages"][sk]["status"]

def _players_cfg():
    """读取『添加AI』配置（rules/ai_apps.json）。

    这是与 players.py（添加AI 写入）和 mix_send.py（实际投递）同一份的配置，
    其 类型 字段区分 本地(electron)/网页(web)，确保本地/WEB 区分与 CDP 端口一致。
    失败（文件缺失/损坏）返回空列表。
    """
    try:
        from players import load_players
        return load_players() or []
    except Exception:
        return []


def available_ais():
    """返回已启用（启用 != False）的 AI 名列表（含本地 electron 与网页 web）。

    来源为『添加AI』配置 rules/ai_apps.json：其 类型 字段区分 本地/网页，
    启用 字段标记是否进入可用池。这样可用池与 mix_send 实际可投递的 AI 完全一致，
    不再读取另一份错位的 windows-use/apps.json。
    """
    ps = _players_cfg()
    if not ps:
        return []
    return [p["名字"] for p in ps
            if p.get("名字") and p.get("启用", True) is not False]


def local_ais():
    """返回可用的『本地』AI 名（类型 == "electron"，即『添加AI』时选的本地端）。

    仅依据『添加AI』对话框里的本地/WEB 选择（类型 字段）来判定，
    不读取被错误标成全 web 的 windows-use/apps.json。

    用于初始化预指派：优先选本地 AI；若配置里没有本地端 AI，
    返回空列表，由调用方回退到 available_ais()（网页端）。
    """
    ps = _players_cfg()
    if not ps:
        return []
    # 优先『已启用』的本地端；全部本地端都没启用时才退回全部本地端
    enabled = [p["名字"] for p in ps
               if p.get("名字") and p.get("类型") == "electron"
               and p.get("启用", True) is not False]
    if enabled:
        return enabled
    return [p["名字"] for p in ps
            if p.get("名字") and p.get("类型") == "electron"]


def all_local_ais():
    """返回全部『本地』AI 名（类型 == "electron"），不论『启用』与否。

    用于审核者/调整者等角色下拉框：指派时让用户能看到并选择所有本地版 AI
    （即使暂时未启用，也可以先指派、稍后在『添加AI』里启用）。
    自动预指派仍用 local_ais()（只用已启用的，避免选到不可投递的）。
    """
    ps = _players_cfg()
    if not ps:
        return []
    return [p["名字"] for p in ps
            if p.get("名字") and p.get("类型") == "electron"]


def new_assignment_state():
    state = {}
    for st in PIPELINE:
        state[st["key"]] = {"label": st["label"], "steps": {}}
        for step in st["steps"]:
            state[st["key"]]["steps"][step["name"]] = {
                "blocks": {b: None for b in step["blocks"]},
                "reviewer": None,
                "adjuster": None,
            }
    return state


def _locate(state, stage_key, step_name):
    st = state.get(stage_key)
    if not st:
        raise KeyError(f"未知环节: {stage_key}")
    step = st["steps"].get(step_name)
    if not step:
        raise KeyError(f"环节 {stage_key} 无子步: {step_name}")
    return step


def assign_block(state, stage_key, step_name, block_name, ai):
    """执行者：ai 可为 str / list / None。"""
    step = _locate(state, stage_key, step_name)
    if block_name not in step["blocks"]:
        raise KeyError(f"子步 {step_name} 无大块: {block_name}")
    if isinstance(ai, list):
        ai = [x for x in ai if x] or None
    step["blocks"][block_name] = ai


def assign_role(state, stage_key, step_name, role, ai):
    """reviewer 可为 str / list / None；adjuster 为 str / None。"""
    if role not in ("reviewer", "adjuster"):
        raise ValueError("role 只能是 reviewer 或 adjuster")
    step = _locate(state, stage_key, step_name)
    if isinstance(ai, list):
        ai = [x for x in ai if x] or None
    step[role] = ai


def save(state, run_state=None, path=DEFAULT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {"pipeline_version": "collab-fixed-5", "assignments": state}
    if run_state is not None:
        data["run_state"] = run_state
    # 原子写：先写临时文件再改名，避免后台线程写盘中途被 UI 线程读到半截文件而崩溃
    tmp = path + ".tmp"
    last_err = None
    for _attempt in range(25):
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
            return path
        except PermissionError as _e:
            # Windows 下目标文件正被其他句柄（如 UI 线程读取）占用时 rename 会失败，
            # 重试若干次等锁释放即可，避免全自动串跑被反复打断。
            last_err = _e
            import time
            time.sleep(0.03)
    if last_err:
        raise last_err
    return path


def load(path=DEFAULT_PATH):
    if not os.path.exists(path):
        return new_assignment_state(), new_run_state()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # 并发读写或文件损坏时返回兜底状态，避免 UI 线程异常崩溃
        return new_assignment_state(), new_run_state()
    base = new_assignment_state()
    saved = data.get("assignments", {})
    for sk, sv in saved.items():
        if sk not in base:
            continue
        for step_name, stepv in sv.get("steps", {}).items():
            if step_name not in base[sk]["steps"]:
                continue
            tgt = base[sk]["steps"][step_name]
            for bk, bv in stepv.get("blocks", {}).items():
                if bk in tgt["blocks"]:
                    tgt["blocks"][bk] = bv
            if stepv.get("reviewer") is not None:
                tgt["reviewer"] = stepv["reviewer"]
            if stepv.get("adjuster") is not None:
                tgt["adjuster"] = stepv["adjuster"]
    run_state = data.get("run_state") or new_run_state()
    for sk in STAGE_ORDER:
        if sk not in run_state.get("stages", {}):
            run_state.setdefault("stages", {})[sk] = {
                "status": "pending", "current_step": None,
                "manual_gate": STAGE_MANUAL_GATE}
    for sk in STAGE_ORDER:
        st = run_state.setdefault("stages", {}).get(sk)
        if st is None:
            run_state["stages"][sk] = {
                "status": "pending", "current_step": None,
                "manual_gate": STAGE_MANUAL_GATE,
                "step_status": {n: "none" for n in _step_names(sk)},
                "item_status": {n: {it: "none" for it in _step_items(sk, n)}
                              for n in _step_names(sk)}}
            continue
        st.setdefault("step_status", {})
        st.setdefault("item_status", {})
        for n in _step_names(sk):
            st["step_status"].setdefault(n, "none")
            st["item_status"].setdefault(n, {})
            for it in _step_items(sk, n):
                st["item_status"][n].setdefault(it, "none")
    enforce_cascade(run_state)
    return base, run_state


# 兼容层
def get_current_key():
    return STAGE_ORDER[0]


def set_current_key(k):
    return k if k in STAGE_ORDER else STAGE_ORDER[0]


def find_link_index(key, links):
    for i, l in enumerate(links):
        if l.get("key") == key:
            return i
    return 0


def refresh_index(links):
    return links


def check_link(link):
    return 0, 1, True


def artifact_dir(ai, link):
    key = (link or {}).get("key") or "x"
    return paths.join("work", "collab", ai, key)


def latest_artifact(ai, link):
    d = artifact_dir(ai, link)
    if not os.path.isdir(d):
        return ""
    files = sorted([f for f in os.listdir(d) if f.endswith((".md", ".json"))],
                   key=lambda f: os.path.getmtime(os.path.join(d, f)))
    if not files:
        return ""
    try:
        return open(os.path.join(d, files[-1]), encoding="utf-8").read()
    except Exception:
        return ""


def upstream_text(link):
    return ""


def _peek_state():
    try:
        s, _ = load()
        return s
    except Exception:
        return new_assignment_state()


def sb_state_blocks(stage_key, step_name):
    s = _peek_state()
    return s.get(stage_key, {}).get("steps", {}).get(step_name, {}).get("blocks", {})


def load_links():
    links = []
    for st in PIPELINE:
        assigned = set()
        for step in st["steps"]:
            for b, ai in sb_state_blocks(st["key"], step["name"]).items():
                if ai:
                    assigned.add(ai)
        links.append({
            "key": st["key"], "name": st["label"],
            "assigned": list(assigned),
            "mode": "single", "inject": False,
            "cmd_dir": "", "check": "", "need": 1,
            "_legacy_proxy": True,
            "desc": st.get("desc", ""),
        })
    return links


def save_links(links):
    return None

def active_sub_keys(stage_key, step_name):
    st = next(s for s in PIPELINE if s["key"] == stage_key)
    step = next(s for s in st["steps"] if s["name"] == step_name)
    if step.get("norms", False):
        return list(SUB_KEYS)
    return [k for k in SUB_KEYS if k not in NORMATIVE_SUBS]


def active_dims(stage_key, step_name):
    subs = active_sub_keys(stage_key, step_name)
    seen = []
    for k in subs:
        d = k.split("·", 1)[0]
        if d not in seen:
            seen.append(d)
    return seen


def build_review_prompt(stage_key, step_name, anon_id, text):
    dims = active_dims(stage_key, step_name)
    subs = active_sub_keys(stage_key, step_name)
    sub_line = "、".join(subs)
    return (
        f"你是一位严格的文学评审，对匿名作品盲审。请仅依据作品质量，"
        f"按维度各打 1-10 分（可含一位小数），并给优点/缺点/修改建议。\n"
        f"启用维度：{'、'.join(dims)}\n"
        f"关注子标准：{sub_line}\n"
        f"作品编号：{anon_id}\n----\n{text[:3500]}\n----\n"
        f"输出 JSON: {{\"scores\":{{...}}, \"pros\":[], \"cons\":[], \"suggestion\":\"\"}}"
    )




class StageBoard:
    """兼容占位类：保留旧 ui_base 对 StageBoard() 的实例化调用。"""

    def __init__(self):
        self.state, self.run_state = load()

if __name__ == "__main__":
    s = new_assignment_state()
    r = new_run_state()
    assign_block(s, "规划", "规划产出", "人物系统", "deepseek")
    set_step_status(r, "写作", "章纲", "pass")
    set_step_status(r, "写作", "正文", "fail")
    assert r["stages"]["写作"]["step_status"]["终审"] == "fail"
    print("stage_all_passed(写作)=", stage_all_passed(r, "写作"))
    r2 = new_run_state()
    for sk, sn in [(st["key"], step["name"]) for st in PIPELINE for step in st["steps"]]:
        set_step_status(r2, sk, sn, "pass")
    for sk in STAGE_ORDER:
        user_passes_gate(r2, sk)
    cascade_fail_from(r2, "写作", "正文")
    assert r2["current_stage"] == "写作"
    assert r2["stages"]["去AI"]["step_status"]["去AI润色"] == "fail"
    assert r2["stages"]["出厂"]["status"] == "pending"
    print("cascade_fail_from OK")
    p = save(s, r)
    print("saved", p)
