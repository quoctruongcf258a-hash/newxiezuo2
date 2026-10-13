"""phase_runner.py — 通用「环节 / 子环」执行引擎。

与 stage_board / auto_stage 正交，基于 rules/assignments.json 的角色指派驱动：

  run_subphase(环节目录, 子环名, 输入文件)
      单子环：生成 task.md（替换 {{输入}}/{{平台规则}}/{{产物目录}}）
              → 执行者 AI 写 output.md
              → 有审核者：审核者 AI 写 review.md
                    · 含 PASS → output.md 复制为 final.md
                    · 含 FAIL → 调整者 AI 写 adjusted.md → final.md
              → 无审核者：output.md 直接复制为 final.md
      返回 final.md 路径。

  run_phase(环节名)
      读 rules/phases.json 该环节有序子环清单，依次 run_subphase，
      前一子环 final.md 作为后一子环输入；全部完成后写
      <环节目录>/放行.json {"confirmed": false} 并停住（等 UI 点放行）。

AI 调用走模块级 CALL_AI(role, ai_name, prompt) -> text；默认是 print 伪实现，
真实环境用 set_call_ai(...) 注入 mix_send 投递即可。
"""

import os
import sys
import json
import shutil
import threading

import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导

# ------------------------------------------------- 暂停 / 断点续跑（跨线程控制）
# UI 点「暂停」→ request_pause()；引擎在每个环（含子项）开跑前检查，
# 置位则写 <环节目录>/暂停.json 并优雅停住（当前环会跑完再停）。
# UI 点「继续」→ clear_pause() 后以 resume=True 重新 run_phase，
# 已有 final.md 的环自动跳过（断点续跑），只补剩下的环。
PAUSE_EVENT = threading.Event()


def request_pause():
    """请求暂停：当前环跑完后停住（写 暂停.json）。"""
    PAUSE_EVENT.set()


def clear_pause():
    """清除暂停请求（继续运行前调用）。"""
    PAUSE_EVENT.clear()


def pause_requested():
    return PAUSE_EVENT.is_set()

# 真实发送层（生产替换 CALL_AI 时再启用）
# sys.path.insert(0, paths.WINDOWS_USE)
# from mix_send import send as _mix_send


# ----------------------------------------------------------------- AI 调用（可替换）
CALL_AI = None  # 默认用内置伪实现


def set_call_ai(fn):
    """注入真实 AI 调用：fn(role, ai_name, prompt, log_fn=print) -> text。"""
    global CALL_AI
    CALL_AI = fn


def _default_call_ai(role, ai_name, prompt, log_fn=print):
    log_fn(f"  [伪AI] {role}（{ai_name}）收到任务，prompt 约 {len(prompt)} 字")
    if role == "审核者":
        return "评审意见：PASS。内容合格，无需修改。"
    if role == "调整者":
        return f"【{ai_name} 调整后稿】\n已根据评审意见修改：(prompt 前80字 {prompt[:80]})"
    return f"【{ai_name} 产出】\n(prompt 前80字 {prompt[:80]})"


def _call_ai(role, ai_name, prompt, log_fn=print):
    fn = CALL_AI or _default_call_ai
    return fn(role, ai_name, prompt, log_fn=log_fn)


# ----------------------------------------------------------------- 配置读取
def _load_platform_rules():
    p = os.path.join(paths.get_cfg_rules_dir(), "platform", "fanqie.json")
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    return ""


def _assign_node(phase_key, sub_name):
    """读 assignments.json，返回 (环节级节点, 子环明细节点)。

    sub_name 可能为 <环名>__<子项码>（子项拆分场景），此处按环名（去 __ 后缀）
    查 明细，使同一环的所有子项共享该环的 AI 指派 / mesh 配置。
    """
    ring_name = sub_name.split("__", 1)[0]
    try:
        with open(os.path.join(paths.get_cfg_rules_dir(), "assignments.json"), encoding="utf-8") as f:
            data = json.load(f) or {}
    except Exception:
        return {}, {}
    stage = data.get("环节", {}).get(phase_key, {}) or {}
    detail = stage.get("明细", {}).get(ring_name, {}) or {}
    return stage, detail


def _lookup_roles(phase_key, sub_name):
    """读 rules/assignments.json：子环明细优先，回退到环节级 执行/审核/调整。"""
    stage, detail = _assign_node(phase_key, sub_name)
    return {
        "执行": detail.get("执行") or stage.get("执行", ""),
        "审核": detail.get("审核") or stage.get("审核", ""),
        "调整": detail.get("调整") or stage.get("调整", ""),
    }


def _lookup_mode(phase_key, sub_name):
    """读该子环的 mode（mesh/human/lock）与赛马配置（writers/judges/merger）。

    这是「第一版 37 环设计」嵌入执行层的入口：
      mesh  = 全网格赛马（N 写手各写 → 匿名交叉盲审 → 汇总择优）
      human = AI 出候选 + 人拍板
      lock  = AI 审计 + 人锁
    读不到 mode 时返回 ""（旧环 / 程序2 原生环节），走原三角色串行逻辑，保持兼容。
    """
    stage, detail = _assign_node(phase_key, sub_name)
    mode = (detail.get("mode") or stage.get("mode") or "").strip()
    def pick(k):
        v = detail.get(k) or stage.get(k) or []
        return v if isinstance(v, list) else ([v] if v else [])
    return mode, {
        "writers": pick("writers"),
        "judges": pick("judges"),
        "merger": detail.get("merger") or stage.get("merger") or "",
        "audit": detail.get("audit") or stage.get("audit") or [],
    }


# ------------------------------------------------- mesh：全网格赛马（核心嵌入）
def _run_mesh(sub_dir, task, roles, mesh, log_fn=print):
    """N 写手各写一份 → 匿名化 → 裁判交叉盲审 → 汇总者择优融合 → final.md。"""
    writers = mesh.get("writers") or ([roles["执行"]] if roles["执行"] else [])
    if not writers:
        log_fn("  ⚠ mesh 环未配置 writers，跳过")
        return None

    # 1) N 写手并行各写一份
    drafts = []
    for i, w in enumerate(writers, 1):
        log_fn(f"  · 写手{i}/{len(writers)}：{w}")
        text = _call_ai(f"写手{i}", w, task, log_fn=log_fn)
        p = os.path.join(sub_dir, f"draft_{i}.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        drafts.append((i, w, text))
    log_fn(f"  ✔ 收齐 {len(drafts)} 份候选稿")

    # 2) 匿名化（剥掉作者标识，避免同源偏置）
    anon = ["# 匿名稿件（不得推测或透露作者）\n"]
    for i, _w, t in drafts:
        anon.append(f"\n===== 稿件 {i} =====\n{t}\n")
    anon_text = "\n".join(anon)
    with open(os.path.join(sub_dir, "_盲审稿.md"), "w", encoding="utf-8") as f:
        f.write(anon_text)
    log_fn("  ✔ 已匿名化（_盲审稿.md）")

    # 3) 交叉盲审：裁判优先用独立 judges，否则写手互审（但看不到自己）
    judges = mesh.get("judges") or writers
    audit = mesh.get("audit") or []
    audit_hint = ("\n评审标准：\n" + "\n".join(f"- {a}" for a in audit)) if audit else ""
    reviews = []
    for j, jd in enumerate(judges, 1):
        prompt = (anon_text + audit_hint +
                  "\n\n请逐份评审，给出：每份的优点/问题、一个整体排序、并明确指出"
                  "【最佳稿编号】与【最差稿编号】。只基于文本质量判断，不要猜测作者。")
        rv = _call_ai(f"裁判{j}", jd, prompt, log_fn=log_fn)
        with open(os.path.join(sub_dir, f"review_{j}.md"), "w", encoding="utf-8") as f:
            f.write(rv + "\n")
        reviews.append((jd, rv))
    log_fn(f"  ✔ 收齐 {len(reviews)} 份盲审")

    # 4) 汇总者择优融合
    merger = mesh.get("merger") or roles.get("调整") or writers[0]
    rv_text = "\n\n".join(f"【{jd} 的评审】\n{rv}" for jd, rv in reviews)
    merge_prompt = (task + "\n\n===== 各匿名候选稿 =====\n" + anon_text +
                    "\n\n===== 各裁判评审意见 =====\n" + rv_text +
                    "\n\n请综合评审意见，取各稿之长，输出一份【融合后的最终版】完整内容。")
    final_text = _call_ai("汇总者", merger, merge_prompt, log_fn=log_fn)
    final_path = os.path.join(sub_dir, "final.md")
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(final_text + "\n")
    log_fn(f"  ✔ mesh 汇总择优完成（汇总者 {merger}）→ final.md")
    return final_path


# ------------------------------------------------- human：AI 出候选 + 人拍板
def _run_human(sub_dir, task, roles, mesh, log_fn=print):
    """AI 出候选稿 → 写 pending.json 停住，等人拍板后才有 final.md。"""
    exec_ai = roles.get("执行") or (mesh.get("writers") or [""])[0]
    if not exec_ai:
        log_fn("  ⚠ human 环未指派执行者，跳过")
        return None
    text = _call_ai("候选生成者", exec_ai, task, log_fn=log_fn)
    cand_path = os.path.join(sub_dir, "candidate.md")
    with open(cand_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    log_fn(f"  ✔ candidate.md（{exec_ai}）")

    final_path = os.path.join(sub_dir, "final.md")
    pending_path = os.path.join(sub_dir, "pending.json")
    chosen = {}
    if os.path.exists(pending_path):
        try:
            chosen = json.load(open(pending_path, encoding="utf-8")) or {}
        except Exception:
            chosen = {}
    if chosen.get("confirmed") and os.path.exists(final_path):
        log_fn("  ✔ 人已拍板 → final.md")
        return final_path
    with open(pending_path, "w", encoding="utf-8") as f:
        json.dump({"confirmed": False, "mode": "human",
                   "candidate": "candidate.md",
                   "hint": "请人工确认 candidate.md；确认后把 confirmed 置 true 并把定稿写为 final.md"},
                  f, ensure_ascii=False, indent=2)
    log_fn("  ⏸ human 环：已出候选，等待人拍板（pending.json）")
    return None


# ------------------------------------------------- lock：AI 审计 + 人锁
def _run_lock(sub_dir, task, roles, mesh, log_fn=print):
    """对已有产出做审计（八方向/质检标准），写 audit.md，等人锁定后才放行。"""
    audit = mesh.get("audit") or []
    src_text = ""
    for cand in ("final.md", "output.md", "candidate.md"):
        p = os.path.join(sub_dir, cand)
        if os.path.exists(p):
            src_text = open(p, encoding="utf-8").read()
            break
    if not src_text and os.path.exists(task):
        src_text = task
    audit_hint = "\n".join(f"- {a}" for a in audit) if audit else "按该环节质量标准逐项检查"
    auditor = (mesh.get("judges") or [roles.get("审核") or roles.get("执行")])[0]
    rv = _call_ai("审计者", auditor,
                  "待审计内容：\n" + src_text + "\n\n审计清单：\n" + audit_hint +
                  "\n\n请逐项给出 通过/不通过 与理由，最后给出总体结论（PASS/FAIL）。",
                  log_fn=log_fn)
    with open(os.path.join(sub_dir, "audit.md"), "w", encoding="utf-8") as f:
        f.write(rv + "\n")
    log_fn(f"  ✔ audit.md（审计者 {auditor}）")

    lock_path = os.path.join(sub_dir, "locked.json")
    locked = {}
    if os.path.exists(lock_path):
        try:
            locked = json.load(open(lock_path, encoding="utf-8")) or {}
        except Exception:
            locked = {}
    if locked.get("locked"):
        final_path = os.path.join(sub_dir, "final.md")
        if not os.path.exists(final_path):
            with open(final_path, "w", encoding="utf-8") as f:
                f.write(src_text + "\n")
        log_fn("  ✔ 人已锁定 → final.md")
        return final_path
    with open(lock_path, "w", encoding="utf-8") as f:
        json.dump({"locked": False, "mode": "lock",
                   "audit": "audit.md",
                   "hint": "请人工审阅 audit.md；通过后把 locked 置 true"},
                  f, ensure_ascii=False, indent=2)
    log_fn("  ⏸ lock 环：审计已完成，等待人锁定（locked.json）")
    return None


# ----------------------------------------------------------------- 单子环
def _fill_extra_placeholders(text, inp, phase_dir):
    """兼容 05_出厂 等旧模板使用的其它占位符。

    老模板写的是 {{项目信息}} / {{上一环节产出}}，引擎原本只替换
    {{输入}}/{{平台规则}}/{{产物目录}}，导致这些占位符原样发给 AI。
    """
    if "{{上一环节产出}}" in text:
        text = text.replace("{{上一环节产出}}", inp or "（无上一环节产出）")
    if "{{项目信息}}" in text:
        info = ""
        d = phase_dir
        for _ in range(3):          # phase_dir 可能是 <项目>/<环节>[/<章号>]
            cand = os.path.join(d, "00_初始化", "项目信息.json")
            if os.path.exists(cand):
                try:
                    info = open(cand, encoding="utf-8").read()
                except Exception:
                    info = ""
                break
            nd = os.path.dirname(d)
            if nd == d:
                break
            d = nd
        text = text.replace("{{项目信息}}", info or inp or "（无项目信息）")
    return text


def run_subphase(phase_dir, sub_name, input_file, log_fn=print, item_desc="",
                 stage_key=None):
    sub_dir = os.path.join(phase_dir, sub_name)
    os.makedirs(sub_dir, exist_ok=True)
    # 章节循环模式下 phase_dir 是 <项目>/<环节>/<章号>，basename 会变成"第001章"，
    # 导致提示词找不到 → 必须由调用方显式传入真正的环节名 stage_key。
    phase_key = stage_key or os.path.basename(phase_dir)

    # 1) task.md：模板替换占位符（按项目配置优先，回退全局）
    ring_base = sub_name.split("/", 1)[0]
    cand_names = [sub_name.replace("/", "__") + ".md"]
    if ring_base != sub_name:
        cand_names.append(ring_base + ".md")
    tpl = ""
    for cand in cand_names:
        tpl_path = paths.cfg_prompt_path(phase_key, cand)
        if os.path.exists(tpl_path):
            tpl = open(tpl_path, encoding="utf-8").read()
            break
    if not tpl.strip():
        # 兜底：回退到本阶段通用模板 _通用.md（37 环模板未逐一补齐时仍可跑，不再整环跳过）
        generic = paths.cfg_prompt_path(phase_key, "_通用.md")
        if os.path.exists(generic):
            tpl = open(generic, encoding="utf-8").read()
            if item_desc:
                tpl = tpl + "\n\n## 本子项专项要求\n" + item_desc
            log_fn(f"  · 子环 {sub_name} 无专属模板，回退 _通用.md" + ("（附子项要求）" if item_desc else ""))
        else:
            # 模板缺失：若有子项要求则直接作为任务，否则视为未配置跳过（不报错）
            if item_desc:
                tpl = "# 子项任务\n" + item_desc
                log_fn(f"  · 子环 {sub_name} 无模板，直接用子项要求作为任务")
            else:
                log_fn(f"  ⊘ 子环 {sub_name} 模板缺失/为空，跳过")
                return None
    inp = ""
    if input_file and os.path.exists(input_file):
        inp = open(input_file, encoding="utf-8").read()
    platform_rules = _load_platform_rules()
    task = (tpl.replace("{{输入}}", inp)
               .replace("{{平台规则}}", platform_rules)
               .replace("{{产物目录}}", sub_dir))
    task = _fill_extra_placeholders(task, inp, phase_dir)
    with open(os.path.join(sub_dir, "task.md"), "w", encoding="utf-8") as f:
        f.write(task)
    log_fn(f"  · task.md 已生成（{sub_name}）")

    roles = _lookup_roles(phase_key, sub_name)
    # 1.5) 第一版 37 环机制嵌入：按 mode 分派执行策略
    mode, mesh = _lookup_mode(phase_key, sub_name)
    if mode in ("mesh", "human", "lock"):
        # mesh/human/lock 由 mode 函数自行取 writers/judges/merger，不要求 执行
        pass
    elif not roles["执行"]:
        log_fn(f"  ⚠ {sub_name} 未指派执行者，跳过产出")
        return None
    if mode == "mesh":
        log_fn(f"  ◆ mode=mesh（全网格赛马：{len(mesh.get('writers') or [])} 写手）")
        return _run_mesh(sub_dir, task, roles, mesh, log_fn=log_fn)
    if mode == "human":
        log_fn("  ◆ mode=human（AI 候选 + 人拍板）")
        return _run_human(sub_dir, task, roles, mesh, log_fn=log_fn)
    if mode == "lock":
        log_fn("  ◆ mode=lock（AI 审计 + 人锁）")
        return _run_lock(sub_dir, task, roles, mesh, log_fn=log_fn)

    # 2) 执行者 → output.md（无 mode 的旧环，保持原三角色串行逻辑）
    output_text = _call_ai("执行者", roles["执行"], task, log_fn=log_fn)
    output_path = os.path.join(sub_dir, "output.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_text + "\n")
    log_fn(f"  ✔ output.md（执行者 {roles['执行']}）")

    final_path = os.path.join(sub_dir, "final.md")

    # 3) 审核者
    if roles["审核"]:
        review_text = _call_ai(
            "审核者", roles["审核"],
            task + "\n\n==== 待评审产出 ====\n" + output_text
            + "\n\n若合格请回复包含 PASS，否则回复包含 FAIL 并给出意见。",
            log_fn=log_fn)
        review_path = os.path.join(sub_dir, "review.md")
        with open(review_path, "w", encoding="utf-8") as f:
            f.write(review_text + "\n")
        log_fn(f"  ✔ review.md（审核者 {roles['审核']}）")
        if "PASS" in review_text:
            shutil.copy(output_path, final_path)
            log_fn(f"  ✔ 审核 PASS → final.md")
        else:
            if roles["调整"]:
                adj_text = _call_ai(
                    "调整者", roles["调整"],
                    "待修改稿：\n" + output_text
                    + "\n\n评审意见：\n" + review_text
                    + "\n\n请输出完整修改稿。", log_fn=log_fn)
                adj_path = os.path.join(sub_dir, "adjusted.md")
                with open(adj_path, "w", encoding="utf-8") as f:
                    f.write(adj_text + "\n")
                log_fn(f"  ✔ adjusted.md（调整者 {roles['调整']}）")
                shutil.copy(adj_path, final_path)
                log_fn(f"  ✔ 审核 FAIL → 调整 → final.md")
            else:
                shutil.copy(output_path, final_path)
                log_fn(f"  ⚠ 审核 FAIL 但无调整者，final 用 output.md")
    else:
        shutil.copy(output_path, final_path)
        log_fn(f"  ✔ 无审核者 → output.md 直接为 final.md")

    return final_path


# ----------------------------------------------------------------- 单大环节
def _ring_final_paths(phase_dir, sub, chapter=None):
    """预估某子环完成后的 final 产物路径（断点续跑判断 / 进度展示共用）。

    返回 (kind, paths)：kind ∈ normal / items / composite。
      normal    → <环节目录>/<环名>/final.md
      items     → 每个子项各自的 final.md
      composite → <环节目录>/<环名>/<章号>_正文.md
    """
    if isinstance(sub, str):
        return "normal", [os.path.join(phase_dir, sub, "final.md")]
    name = (sub.get("name") or "")
    items = sub.get("items")
    if items:
        ps = []
        for it in items:
            code = it.get("code") or it.get("name") or "item"
            ps.append(os.path.join(phase_dir, "%s__%s" % (name, code), "final.md"))
        return "items", ps
    if sub.get("segments"):
        chap_nm = sub.get("chapter") or chapter or "第001章"
        return "composite", [os.path.join(phase_dir, name, "%s_正文.md" % chap_nm)]
    return "normal", [os.path.join(phase_dir, name, "final.md")]


def _write_pause_marker(phase_dir, phase_name, log_fn):
    with open(os.path.join(phase_dir, "暂停.json"), "w", encoding="utf-8") as f:
        json.dump({"paused": True, "phase": phase_name,
                   "hint": "已暂停；调整指派后点【继续】将从断点续跑（已完成环自动跳过）"},
                  f, ensure_ascii=False, indent=2)
    log_fn("⏸ 已暂停（写 暂停.json）。可重新 🎯AI指派 换选手/评委，再点【⏯ 继续】从断点续跑。")


def run_phase(phase_name, log_fn=print, project_dir=None, finalize=None, resume=False,
              chapter=None):
    """串跑某环节所有子环（前子环 final 作后子环输入），末尾写 放行.json 并停住。
    finalize(phase_dir, subs, finals, log_fn) 为环节级收尾钩子（如八方向审核/汇总）。

    resume=True：断点续跑——已有 final 产出的子环直接跳过（配合暂停后换指派继续）。
    暂停：环间检查 PAUSE_EVENT，置位则写 <环节目录>/暂停.json 并返回 "PAUSED"。
    chapter：章节循环模式——产物落到 <project>/<环节>/<章号>/ 下（02/03/04 每章一轮）。

    subs 元素可为字符串（普通子环）或 dict：
      · {"name", "segments":[...], "chapter"}：复合子环——按 segments 顺序各跑一次
        run_subphase（输入=上段 final + 锁定章纲），最后把各段 final 拼成 <chapter>_正文.md。
      · {"name", "input":"相对项目根的文件路径"}：单子环但用显式共享输入（不链式，
        每个子环都吃同一份输入，如 环节4 各子环都吃润色定稿）。"""
    # 解析 环节目录（章节循环模式：产物落到 <环节>/<章号>/ 下）
    if project_dir:
        base_dir = os.path.join(project_dir, phase_name)
    else:
        base_dir = paths.workspace_path(phase_name)
    phase_dir = os.path.join(base_dir, chapter) if chapter else base_dir
    os.makedirs(phase_dir, exist_ok=True)

    # 子环清单（有序）
    try:
        with open(os.path.join(paths.get_cfg_rules_dir(), "phases.json"), encoding="utf-8") as f:
            data = json.load(f) or {}
    except Exception as e:
        log_fn(f"❌ 读取 phases.json 失败：{e}")
        return None
    subs = data.get("环节", {}).get(phase_name)
    if not subs:
        log_fn(f"❌ phases.json 无环节 {phase_name}")
        return None

    log_fn(f"=== 环节【{phase_name}】开始（{len(subs)} 子环/段组）===")
    # 首个子环的输入文件（优先子环目录内 input.md，其次环节级 input.md）
    first = subs[0] if isinstance(subs[0], str) else subs[0].get("name", "")
    inp = None
    for cand in (os.path.join(phase_dir, first, "input.md"),
                os.path.join(phase_dir, "input.md")):
        if os.path.exists(cand):
            inp = cand
            break
    prev_final = inp
    finals = []
    for sub in subs:
        # 暂停检查：置位则停住（断点天然存在——未跑的环没有 final.md）
        if PAUSE_EVENT.is_set():
            _write_pause_marker(phase_dir, phase_name, log_fn)
            return "PAUSED"
        # 断点续跑：该环全部 final 已存在则跳过（不重跑、不覆盖）
        if resume:
            kind, exp = _ring_final_paths(phase_dir, sub, chapter)
            if exp and all(os.path.exists(p) for p in exp):
                nm = sub if isinstance(sub, str) else (sub.get("name") or "")
                log_fn(f"↩ 断点续跑：{nm} 已有产出，跳过")
                if kind in ("normal", "composite"):
                    prev_final = exp[0]
                    finals.append((nm, exp[0]))
                continue
        if isinstance(sub, dict):
            name = sub.get("name")
            items = sub.get("items")
            if items:
                # 子项拆分（赛马「细」的另一半）：同一环拆成多个独立子项，
                # 每个子项 = 一个文件（如 一句话故事/B1-1/final.md），均吃本环节入参。
                # 各子项独立跑 mesh/human/lock/串行，互不复用前子项输出。
                log_fn(f"-- 环节内子项拆分：{name}（{len(items)} 子项）--")
                for it in items:
                    if PAUSE_EVENT.is_set():
                        _write_pause_marker(phase_dir, phase_name, log_fn)
                        return "PAUSED"
                    code = it.get("code") or it.get("name") or "item"
                    item_name = it.get("name") or code
                    item_desc = it.get("desc", "")
                    sub_name = f"{name}__{code}"
                    if resume and os.path.exists(
                            os.path.join(phase_dir, sub_name, "final.md")):
                        log_fn(f"  ↩ 断点续跑：子项 {code} 已有产出，跳过")
                        finals.append((f"{name}/{code}",
                                       os.path.join(phase_dir, sub_name, "final.md")))
                        continue
                    log_fn(f"  · 子项 {code}（{item_name}）")
                    final = run_subphase(phase_dir, sub_name, prev_final,
                                         item_desc=item_desc, log_fn=log_fn,
                                         stage_key=phase_name)
                    if final is None:
                        log_fn(f"  ⊘ 子项 {code} 跳过（未配置/无产出）")
                        continue
                    finals.append((f"{name}/{code}", final))
                # 子项不链式，环节入参保持不变，传给下一环
                continue
            segs = sub.get("segments")
            name = sub.get("name")
            segs = sub.get("segments")
            if not segs:
                # 单子环 + 显式共享输入（如 环节4 各子环都吃润色定稿）
                inp = sub.get("input")
                input_file = None
                if inp:
                    if project_dir:
                        input_file = os.path.join(project_dir, *inp.split("/"))
                    else:
                        input_file = os.path.join(paths.workspace_path(phase_name), *inp.split("/"))
                log_fn(f"-- 子环 {name}（共享输入：{inp or '无'}）--")
                final = run_subphase(phase_dir, name, input_file, log_fn=log_fn,
                                     stage_key=phase_name)
                if final is None:
                    log_fn(f"  ⊘ 子环 {name} 跳过（未配置/无产出）")
                    continue
                finals.append((name, final))
                prev_final = final
                continue
            # 复合子环：按 segments 顺序跑，每段独立 run_subphase，最后拼成单章
            chap_nm = sub.get("chapter") or chapter or "第001章"
            log_fn(f"-- 复合子环 {name}（{len(segs)} 段：{'→'.join(segs)}）--")
            locked = _read_locked_chapter(project_dir)
            seg_finals = []
            for seg in segs:
                seg_name = f"{name}/{seg}"
                log_fn(f"  · 段 {seg}（{seg_name}）")
                # 输入 = 上一段 final + 锁定章纲
                in_text = ""
                if prev_final and os.path.exists(prev_final):
                    in_text += open(prev_final, encoding="utf-8").read().strip() + "\n\n"
                if locked:
                    in_text += "# 锁定章纲（章纲_锁定版）\n" + locked + "\n\n"
                seg_input_path = os.path.join(phase_dir, name, f"__{seg}__input.md")
                os.makedirs(os.path.dirname(seg_input_path), exist_ok=True)
                with open(seg_input_path, "w", encoding="utf-8") as f:
                    f.write(in_text)
                sfinal = run_subphase(phase_dir, seg_name, seg_input_path,
                                      log_fn=log_fn, stage_key=phase_name)
                if sfinal is None:
                    log_fn(f"  ⊘ 段 {seg} 跳过（未配置/无产出）")
                    continue
                seg_finals.append(sfinal)
                prev_final = sfinal
            body = ""
            for fp in seg_finals:
                if os.path.exists(fp):
                    body += open(fp, encoding="utf-8").read().strip() + "\n\n"
            chapter_path = os.path.join(phase_dir, name, f"{chap_nm}_正文.md")
            os.makedirs(os.path.dirname(chapter_path), exist_ok=True)
            with open(chapter_path, "w", encoding="utf-8") as f:
                f.write(body)
            log_fn(f"  ✔ 已拼接 {os.path.basename(chapter_path)}（{len(seg_finals)} 段）")
            final = chapter_path
            finals.append((name, final))
        else:
            # 普通子环
            log_fn(f"-- 子环 {sub} --")
            final = run_subphase(phase_dir, sub, prev_final, log_fn=log_fn,
                                 stage_key=phase_name)
            if final is None:
                log_fn(f"  ⊘ 子环 {sub} 跳过（未配置/无产出）")
                continue
            finals.append((sub, final))
            prev_final = final

    # 环节级收尾（汇总/交付等，由调用方注入）
    if finalize:
        try:
            finalize(phase_dir, subs, finals, log_fn=log_fn)
        except Exception as e:
            log_fn(f"❌ 环节收尾失败：{e}")

    # 末尾写 放行.json 并停住（等 UI 点放行）；正常完成则清掉暂停标记
    try:
        pz = os.path.join(phase_dir, "暂停.json")
        if os.path.exists(pz):
            os.remove(pz)
    except Exception:
        pass
    release = {"confirmed": False}
    if chapter:
        release["chapter"] = chapter
    with open(os.path.join(phase_dir, "放行.json"), "w", encoding="utf-8") as f:
        json.dump(release, f, ensure_ascii=False, indent=2)
    log_fn(f"=== 环节【{phase_name}】完成，已写 放行.json（confirmed=false），等待 UI 放行 ===")
    return os.path.join(phase_dir, "放行.json")


# ------------------------------------------------- 章节循环编排（全书跑法）
LOOP_PHASES = ("02_写作", "03_去AI", "04_审核")
ONCE_PHASES = ("01_规划", "05_出厂")


def run_book(project_dir, chapters=1, log_fn=print, resume=False, start_chapter=1):
    """32流程版·全书编排：
        01_规划（一次性 23 环）
        → 每章循环：02_写作(4) → 03_去AI(1) → 04_审核(9)   ← 循环一次加一章
        → 05_出厂（一次性）
    每轮循环的产物落到 <环节>/<章号>/ 下；支持暂停（环间生效）与断点续跑。
    返回 "PAUSED" 或最后一段放行.json 路径。
    """
    order = ["01_规划"]
    for ch in range(start_chapter, chapters + 1):
        order += [("02_写作", "第%03d章" % ch), ("03_去AI", "第%03d章" % ch),
                  ("04_审核", "第%03d章" % ch)]
    order.append("05_出厂")
    log_fn(f"📚 全书编排：规划1轮 + 正文循环 {chapters} 章（写作4+润色1+审核9 / 章）+ 出厂1轮")

    last = None
    for item in order:
        if PAUSE_EVENT.is_set():
            phase_name = item if isinstance(item, str) else item[0]
            _write_pause_marker(os.path.join(project_dir, phase_name), phase_name, log_fn)
            return "PAUSED"
        if isinstance(item, str):
            phase_name, chapter = item, None
        else:
            phase_name, chapter = item
        # 断点续跑：该轮放行已确认则整轮跳过
        base = os.path.join(project_dir, phase_name)
        round_dir = os.path.join(base, chapter) if chapter else base
        rel = os.path.join(round_dir, "放行.json")
        if resume and os.path.exists(rel):
            try:
                if (json.load(open(rel, encoding="utf-8")) or {}).get("confirmed"):
                    log_fn(f"↩ 断点续跑：{phase_name}" + (f"/{chapter}" if chapter else "") + " 已放行，跳过")
                    last = rel
                    continue
            except Exception:
                pass
        log_fn("▶▶ " + phase_name + (f" / {chapter}" if chapter else ""))
        out = run_phase(phase_name, log_fn=log_fn, project_dir=project_dir,
                        resume=resume, chapter=chapter)
        if out == "PAUSED":
            return "PAUSED"
        last = out
    return last


def _read_locked_chapter(project_dir):
    """读 01_规划 锁定章纲，作为正文撰写的输入锚点（若未生成则返回空串）。"""
    if project_dir:
        p = os.path.join(project_dir, "01_规划", "章纲_锁定版.md")
    else:
        p = os.path.join(paths.workspace_path("01_规划"), "章纲_锁定版.md")
    if os.path.exists(p):
        try:
            return open(p, encoding="utf-8").read()
        except Exception:
            return ""
    return ""


# ----------------------------------------------------------------- 通用生成（角色评审/调整步骤）
def generate(phase_dir, template_name, input_text, role_key, out_name=None,
             log_fn=print, stage_key=None):
    """读模板→替换占位符→调 CALL_AI(role_key)→写文件。返回文本或 None（跳过）。

    用于 环节级 收尾：如 _审核者(八方向审核)→review.md、_调整者→adjusted.md。
    role_key 取 assignments 的 执行/审核/调整。
    stage_key：章节循环模式下须显式传环节名（phase_dir 的 basename 是"第NN章"）。"""
    phase_key = stage_key or os.path.basename(phase_dir)
    tpl_path = paths.cfg_prompt_path(phase_key, template_name + ".md")
    if os.path.exists(tpl_path):
        tpl = open(tpl_path, encoding="utf-8").read()
    else:
        tpl = ""
    if not tpl.strip():
        log_fn(f"  ⊘ 模板 {template_name} 缺失/为空，跳过")
        return None
    inp = input_text or ""
    platform_rules = _load_platform_rules()
    prompt = (tpl.replace("{{输入}}", inp)
                 .replace("{{平台规则}}", platform_rules)
                 .replace("{{产物目录}}", phase_dir))
    prompt = _fill_extra_placeholders(prompt, inp, phase_dir)
    roles = _lookup_roles(phase_key, template_name)
    ai_name = roles.get(role_key) or ""
    if not ai_name:
        log_fn(f"  ⚠ {template_name} 未指派{role_key}，跳过")
        return None
    text = _call_ai(role_key, ai_name, prompt, log_fn=log_fn)
    out = out_name or (template_name + ".md")
    out_path = os.path.join(phase_dir, *out.split("/"))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    log_fn(f"  ✔ 已生成 {out}（{role_key}：{ai_name}）")
    return text


# ----------------------------------------------------------------- 假数据自测
if __name__ == "__main__":
    # GBK 控制台无法编码 emoji，统一 utf-8 容错（GUI 走 QTextEdit 不受影响）
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    import tempfile
    import shutil as _sh

    # 用临时目录假数据测试，不污染真实 workspace / prompts
    tmp = tempfile.mkdtemp(prefix="phase_test_")
    proj = os.path.join(tmp, "假项目_2026-10-08")
    phase_dir = os.path.join(proj, "01_规划")
    subs = ["1-1_定位与卖点", "1-2_故事核心与主题", "1-3_人物系统", "1-4_世界与设定",
            "1-5_结构与节奏", "1-6_章纲清单", "1-7_上架包装"]
    for s in subs:
        os.makedirs(os.path.join(phase_dir, s), exist_ok=True)
    # input.md 放在第一个子环目录
    with open(os.path.join(phase_dir, subs[0], "input.md"), "w", encoding="utf-8") as f:
        f.write("# 初始输入\n这是项目初始化信息，用于规划环节。\n")

    # 临时 prompts 模板（覆盖 prompt 查找根，不影响真实文件）
    tprompts = os.path.join(tmp, "prompts")
    os.makedirs(os.path.join(tprompts, "01_规划"), exist_ok=True)
    for s in subs:
        with open(os.path.join(tprompts, "01_规划", s + ".md"), "w", encoding="utf-8") as f:
            f.write("【子环任务】\n输入：\n{{输入}}\n\n平台规则：\n{{平台规则}}\n\n产物目录：{{产物目录}}\n")
    paths.PROMPTS_DIR = tprompts

    # 默认伪 AI（print，不真调）
    set_call_ai(None)

    out = run_phase("01_规划", log_fn=print, project_dir=proj)

    # 验收检查
    ok = True
    for s in subs:
        fp = os.path.join(phase_dir, s, "final.md")
        if not os.path.exists(fp):
            print(f"✖ 缺失 final: {s}")
            ok = False
    rel = os.path.join(phase_dir, "放行.json")
    rel_ok = os.path.exists(rel)
    if rel_ok:
        with open(rel, encoding="utf-8") as f:
            rd = json.load(f)
        rel_ok = (rd.get("confirmed") is False)
    print("== 验收 ==")
    print(f"  7 子环 final.md 全部存在: {ok}")
    print(f"  放行.json 存在且 confirmed=false: {rel_ok}")
    print(f"  未真调 AI，无报错。")

    # 额外验证 FAIL → 调整 → final 分支（不计入主验收）
    def _fail_ai(role, ai_name, prompt, log_fn=print):
        if role == "审核者":
            return "评审意见：FAIL。第二段节奏偏平，请加强冲突。"
        return _default_call_ai(role, ai_name, prompt, log_fn=log_fn)
    set_call_ai(_fail_ai)
    sub_dir = os.path.join(phase_dir, "_FAIL测试")
    os.makedirs(sub_dir, exist_ok=True)
    with open(os.path.join(sub_dir, "input.md"), "w", encoding="utf-8") as f:
        f.write("测试输入\n")
    with open(os.path.join(tprompts, "01_规划", "_FAIL测试.md"), "w", encoding="utf-8") as f:
        f.write("【任务】\n{{输入}}\n平台规则：\n{{平台规则}}\n产物目录：{{产物目录}}\n")
    run_subphase(phase_dir, "_FAIL测试", os.path.join(sub_dir, "input.md"), log_fn=print)
    fail_ok = (os.path.exists(os.path.join(sub_dir, "adjusted.md"))
               and os.path.exists(os.path.join(sub_dir, "final.md")))
    print(f"  FAIL→调整 分支: adjusted.md & final.md 存在 = {fail_ok}")

    _sh.rmtree(tmp, ignore_errors=True)
