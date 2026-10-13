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

import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导

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
    p = os.path.join(paths.RULES_DIR, "platform", "fanqie.json")
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    return ""


def _lookup_roles(phase_key, sub_name):
    """读 rules/assignments.json：子环明细优先，回退到环节级 执行/审核/调整。"""
    try:
        with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
            data = json.load(f) or {}
    except Exception:
        return {"执行": "", "审核": "", "调整": ""}
    stage = data.get("环节", {}).get(phase_key, {})
    detail = stage.get("明细", {}).get(sub_name, {}) or {}
    return {
        "执行": detail.get("执行") or stage.get("执行", ""),
        "审核": detail.get("审核") or stage.get("审核", ""),
        "调整": detail.get("调整") or stage.get("调整", ""),
    }


# ----------------------------------------------------------------- 单子环
def run_subphase(phase_dir, sub_name, input_file, log_fn=print):
    sub_dir = os.path.join(phase_dir, sub_name)
    os.makedirs(sub_dir, exist_ok=True)
    phase_key = os.path.basename(phase_dir)

    # 1) task.md：模板替换占位符
    tpl_path = paths.prompt_path(phase_key, sub_name + ".md")
    if os.path.exists(tpl_path):
        tpl = open(tpl_path, encoding="utf-8").read()
    else:
        tpl = ""
    if not tpl.strip():
        # 模板缺失/为空 = 该子环尚未配置，跳过（不报错，便于"先填 3 个再补 4 个"）
        log_fn(f"  ⊘ 子环 {sub_name} 模板缺失/为空，跳过")
        return None
    inp = ""
    if input_file and os.path.exists(input_file):
        inp = open(input_file, encoding="utf-8").read()
    platform_rules = _load_platform_rules()
    task = (tpl.replace("{{输入}}", inp)
               .replace("{{平台规则}}", platform_rules)
               .replace("{{产物目录}}", sub_dir))
    with open(os.path.join(sub_dir, "task.md"), "w", encoding="utf-8") as f:
        f.write(task)
    log_fn(f"  · task.md 已生成（{sub_name}）")

    roles = _lookup_roles(phase_key, sub_name)
    if not roles["执行"]:
        log_fn(f"  ⚠ {sub_name} 未指派执行者，跳过产出")
        return None

    # 2) 执行者 → output.md
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
def run_phase(phase_name, log_fn=print, project_dir=None, finalize=None):
    """串跑某环节所有子环（前子环 final 作后子环输入），末尾写 放行.json 并停住。
    finalize(phase_dir, subs, finals, log_fn) 为环节级收尾钩子（如八方向审核/汇总）。

    subs 元素可为字符串（普通子环）或 dict：
      · {"name", "segments":[...], "chapter"}：复合子环——按 segments 顺序各跑一次
        run_subphase（输入=上段 final + 锁定章纲），最后把各段 final 拼成 <chapter>_正文.md。
      · {"name", "input":"相对项目根的文件路径"}：单子环但用显式共享输入（不链式，
        每个子环都吃同一份输入，如 环节4 各子环都吃润色定稿）。"""
    # 解析 环节目录
    if project_dir:
        phase_dir = os.path.join(project_dir, phase_name)
    else:
        phase_dir = paths.workspace_path(phase_name)
    os.makedirs(phase_dir, exist_ok=True)

    # 子环清单（有序）
    try:
        with open(os.path.join(paths.RULES_DIR, "phases.json"), encoding="utf-8") as f:
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
        if isinstance(sub, dict):
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
                final = run_subphase(phase_dir, name, input_file, log_fn=log_fn)
                if final is None:
                    log_fn(f"  ⊘ 子环 {name} 跳过（未配置/无产出）")
                    continue
                finals.append((name, final))
                prev_final = final
                continue
            # 复合子环：按 segments 顺序跑，每段独立 run_subphase，最后拼成单章
            chapter = sub.get("chapter", "第001章")
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
                sfinal = run_subphase(phase_dir, seg_name, seg_input_path, log_fn=log_fn)
                if sfinal is None:
                    log_fn(f"  ⊘ 段 {seg} 跳过（未配置/无产出）")
                    continue
                seg_finals.append(sfinal)
                prev_final = sfinal
            body = ""
            for fp in seg_finals:
                if os.path.exists(fp):
                    body += open(fp, encoding="utf-8").read().strip() + "\n\n"
            chapter_path = os.path.join(phase_dir, name, f"{chapter}_正文.md")
            os.makedirs(os.path.dirname(chapter_path), exist_ok=True)
            with open(chapter_path, "w", encoding="utf-8") as f:
                f.write(body)
            log_fn(f"  ✔ 已拼接 {os.path.basename(chapter_path)}（{len(seg_finals)} 段）")
            final = chapter_path
            finals.append((name, final))
        else:
            # 普通子环
            log_fn(f"-- 子环 {sub} --")
            final = run_subphase(phase_dir, sub, prev_final, log_fn=log_fn)
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

    # 末尾写 放行.json 并停住（等 UI 点放行）
    release = {"confirmed": False}
    with open(os.path.join(phase_dir, "放行.json"), "w", encoding="utf-8") as f:
        json.dump(release, f, ensure_ascii=False, indent=2)
    log_fn(f"=== 环节【{phase_name}】完成，已写 放行.json（confirmed=false），等待 UI 放行 ===")
    return os.path.join(phase_dir, "放行.json")


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
def generate(phase_dir, template_name, input_text, role_key, out_name=None, log_fn=print):
    """读模板→替换占位符→调 CALL_AI(role_key)→写文件。返回文本或 None（跳过）。

    用于 环节级 收尾：如 _审核者(八方向审核)→review.md、_调整者→adjusted.md。
    role_key 取 assignments 的 执行/审核/调整。"""
    phase_key = os.path.basename(phase_dir)
    tpl_path = paths.prompt_path(phase_key, template_name + ".md")
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
