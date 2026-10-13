"""流水线执行器：根据 stage.action 执行具体操作"""
import os, time, sys, re
import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导
sys.path.insert(0, paths.WINDOWS_USE)
from pipeline import STAGES, KEY2STAGE, AIS, ROOT, CMD_ROOT

# ===== 程序二·协同写作 扩展（仅新增，不改既有 action） =====
DRY_RUN = False


def set_dry_run(v):
    """dry_run=True：走 core.delivery 模拟发送并落占位产物，便于无窗口验证整条环节编排。"""
    global DRY_RUN
    DRY_RUN = bool(v)


from stage_board import (COLLAB_ROOT, upstream_text, latest_artifact, artifact_dir)


def _send(ai, text, log_fn):
    from mix_send import send
    try:
        r = send(ai, text)
        log_fn(f"  {r}")
        return True
    except Exception as e:
        log_fn(f"  ❌ {ai}: {e}")
        return False



def _count_files(ai, check, prefix, need):
    """算某 AI 在当前阶段的达标文件数"""
    if check.startswith("_融合产物"):
        d = os.path.join(ROOT, check)
    else:
        d = os.path.join(ROOT, ai, check)
    if not os.path.isdir(d): return 0
    n = 0
    for f in os.listdir(d):
        if not f.endswith((".md", ".json")): continue
        if prefix and not f.startswith(prefix): continue
        try:
            if os.path.getsize(os.path.join(d, f)) >= 500:
                n += 1
        except: pass
    return n


def _incomplete_ais(stage):
    """返回未达标的 AI 列表"""
    check = stage.get("check", "")
    prefix = stage.get("prefix", "")
    need = stage.get("need", 1)
    bad = []
    for ai in AIS:
        if _count_files(ai, check, prefix, need) < need:
            bad.append(ai)
    return bad


def _batch_targets(fp):
    """读批次文件，返回该批要评审的对手名列表
    兼容两种格式:
      1) 规划轮: ########## 对手：XXX ##########
      2) 润色轮: 本次你将审阅**编号 XXX 选手**
    """
    try:
        txt = open(fp, encoding="utf-8").read()
    except Exception:
        return []
    t = re.findall(r"#{3,}\s*对手[：:]\s*(\S+?)\s*#{3,}", txt)
    if t:
        return t
    return re.findall(r"编号\s*\**\s*([A-Za-z]+)\s*\**\s*选手", txt)


def _batch_done(ai, check, batch_no, targets):
    """判断批次 batch_no 是否已完成
    任意一个成立即算完成:
      a) 同名 {ai}_第N批.md / .json 存在
      b) targets 不为空且都已有 评审_X.md
    """
    d = os.path.join(ROOT, ai, check)
    for ext in (".md", ".json"):
        if os.path.exists(os.path.join(d, ai + "_第" + str(batch_no) + "批" + ext)):
            return True
    if not targets:
        return False
    done = _done_targets(ai, check)
    return all(t in done for t in targets)


def _done_targets(ai, check):
    """扫该家落盘目录，返回已完成的对手名集合"""
    d = os.path.join(ROOT, ai, check)
    done = set()
    if not os.path.isdir(d):
        return done
    for f in os.listdir(d):
        if not f.endswith((".md", ".json")):
            continue
        m = re.match(r"评审_(.+)\.(md|json)$", f)
        if m:
            done.add(m.group(1))
    return done


def _md_names(d):
    if not os.path.isdir(d):
        return set()
    return set(f for f in os.listdir(d) if f.endswith((".md", ".json")))


def execute_stage(stage_key, log_fn):
    """执行当前阶段；stage_key 可为阶段 key(字符串，程序一) 或环节 dict(程序二)。"""
    if isinstance(stage_key, dict):
        s = stage_key
    else:
        s = KEY2STAGE.get(stage_key)
    if not s:
        log_fn(f"❌ 未知阶段: {stage_key}")
        return 0, 0

    action = s.get("action", "assigned")
    if action != "assigned":
        cmd_dir = os.path.join(CMD_ROOT, s["cmd_dir"])
        if not os.path.isdir(cmd_dir):
            log_fn(f"❌ 指令目录不存在: {cmd_dir}")
            return 0, 0

    # 广播所有 AI（每份独立文件）——只发未达标的
    if action == "broadcast":
        incomplete = _incomplete_ais(s)
        if not incomplete:
            log_fn("✅ 全部已达标，无需广播")
            return len(AIS), len(AIS)
        log_fn(f"📤 只发未达标 {len(incomplete)} 家：{incomplete}")
        ok = 0
        for i, ai in enumerate(incomplete, 1):
            fp = os.path.join(cmd_dir, f"{ai}.txt")
            if not os.path.exists(fp):
                log_fn(f"[{i}/{len(incomplete)}] {ai}: 无文件")
                continue
            text = open(fp, encoding="utf-8").read()
            kb = len(text.encode("utf-8")) // 1024
            log_fn(f"[{i}/{len(incomplete)}] → {ai} ({kb}KB)")
            if _send(ai, text, log_fn): ok += 1
            time.sleep(3)
        return ok, len(incomplete)

    # 分批广播（互审类）——批级串行 + 30分钟窗口 + 超时重发本批
    if action == "broadcast_batch":
        WINDOW_SEC = 30 * 60
        POLL_SEC = 15
        log_fn("📤 分批广播（批级串行，每批 30 分钟窗口）")
        for ai in AIS:
            batches = sorted([f for f in os.listdir(cmd_dir)
                              if f.startswith(ai + "_") and f.endswith(".txt")])
            if not batches:
                log_fn("  " + ai + ": 无批次文件")
                continue
            log_fn("  === " + ai + "：" + str(len(batches)) + " 批 ===")
            for k, fn in enumerate(batches, 1):
                fp = os.path.join(cmd_dir, fn)
                try:
                    text = open(fp, encoding="utf-8").read()
                except Exception as e:
                    log_fn("    ❌ 读 " + fn + " 失败: " + str(e))
                    continue
                targets = _batch_targets(fp)
                kb = len(text.encode("utf-8")) // 1024
                if not targets:
                    log_fn("    → " + ai + " 第" + str(k) + "批 " + fn + " (" + str(kb) + "KB，无法解析对手，仅发一次)")
                    _send(ai, text, log_fn)
                    time.sleep(3)
                    continue
                if _batch_done(ai, s["check"], k, targets):
                    log_fn("    ✅ " + ai + " 第" + str(k) + "批 已齐，跳过")
                    continue
                desc = ("目标 " + "/".join(targets)) if targets else "无解析目标"
                while True:
                    log_fn("    → " + ai + " 第" + str(k) + "批 " + fn + " (" + str(kb) + "KB, " + desc + ")")
                    _send(ai, text, log_fn)
                    t0 = time.time()
                    finish = False
                    while time.time() - t0 < WINDOW_SEC:
                        time.sleep(POLL_SEC)
                        if _batch_done(ai, s["check"], k, targets):
                            log_fn("    ✅ " + ai + " 第" + str(k) + "批 已齐 (耗时 " + str(int(time.time()-t0)) + "s)")
                            finish = True
                            break
                    if finish:
                        break
                    log_fn("    ⚠ " + ai + " 第" + str(k) + "批 超 30 分钟未齐，重发本批")
        return len(AIS), len(AIS)

    # 融合（单发给 ZCode）
    if action == "merge":
        files = sorted([f for f in os.listdir(cmd_dir) if f.endswith(".txt")])
        if not files:
            log_fn(f"❌ 融合指令目录空: {cmd_dir}")
            return 0, 1
        WINDOW_SEC = 30 * 60
        POLL_SEC = 15
        target_dir = os.path.join(ROOT, s["check"])
        log_fn(f"📤 融合（批级串行，目标: {s['check']}）")
        ok = 0
        for k, fn in enumerate(files, 1):
            text = open(os.path.join(cmd_dir, fn), encoding="utf-8").read()
            kb = len(text.encode("utf-8")) // 1024
            while True:
                before = _md_names(target_dir)
                log_fn(f"→ ZCode 融合第{k}批 ({kb}KB)")
                if _send("ZCode", text, log_fn):
                    ok += 1
                t0 = time.time()
                finish = False
                while time.time() - t0 < WINDOW_SEC:
                    time.sleep(POLL_SEC)
                    if _md_names(target_dir) - before:
                        log_fn(f"  ✅ 第{k}批 已落盘 (耗时 {int(time.time()-t0)}s)")
                        finish = True
                        break
                if finish:
                    break
                log_fn(f"  ⚠ 第{k}批 超 30 分钟未落盘，重发本批")
        return ok, len(files)

    # 单份广播（终审类，所有 AI 用同一份）——只发未达标的
    if action == "broadcast_one":
        incomplete = _incomplete_ais(s)
        if not incomplete:
            log_fn("✅ 全部已达标，无需广播")
            return len(AIS), len(AIS)
        log_fn(f"📤 只发未达标 {len(incomplete)} 家：{incomplete}")
        fname = s.get("file", "公共.txt")
        fp = os.path.join(cmd_dir, fname)
        if not os.path.exists(fp):
            # 找目录里任意一个 .txt
            files = [f for f in os.listdir(cmd_dir) if f.endswith(".txt")]
            if not files:
                log_fn(f"❌ 找不到 {fname}")
                return 0, 0
            fp = os.path.join(cmd_dir, files[0])
        text = open(fp, encoding="utf-8").read()
        kb = len(text.encode("utf-8")) // 1024
        ok = 0
        for i, ai in enumerate(incomplete, 1):
            log_fn(f"[{i}/{len(incomplete)}] → {ai} ({kb}KB)")
            if _send(ai, text, log_fn): ok += 1
            time.sleep(4)
        return ok, len(incomplete)

    # 程序二·指派编排：只发该环节 assigned 的 AI，并注入上游产物
    if action == "assigned":
        return _run_assigned(s, log_fn)

    log_fn(f"❌ 未知 action: {action}")
    return 0, 0


# ---------- 程序二·指派编排 辅助 ----------
def _send_assigned(ai, text, log_fn, link):
    """指派发送：dry_run 直接模拟并落占位产物；real 走 core.delivery.dispatch 既有签名。"""
    if DRY_RUN:
        log_fn(f"  [dry] {ai}: 模拟发送 {len(text)} 字")
        _sim_drop(ai, link, text)
        return True
    try:
        from core.delivery import dispatch
        r = dispatch(ai, text, dry_run=False)
        log_fn(f"  {ai}: status={r.get('status')} source={r.get('source')}")
        return r.get("status") == "ok"
    except Exception as e:
        log_fn(f"  ❌ {ai}: {e}")
        return False


def _sim_drop(ai, link, text):
    """dry-run 下写入占位产物，使 check_link 能自洽推进（非真实 AI 输出）。"""
    d = artifact_dir(ai, link)
    try:
        os.makedirs(d, exist_ok=True)
        fn = f"{ai}_{link.get('key', 'x')}_dry.md"
        with open(os.path.join(d, fn), "w", encoding="utf-8") as f:
            f.write(f"【{ai} dry 模拟产出】环节={link.get('name', '')}\n\n"
                    f"{text[:300]}\n\n（dry-run 占位，非真实 AI 输出）")
    except Exception:
        pass


def _build_prompt(cmd_dir, ai, link, upstream):
    """组装发送文本：优先读 cmd_dir/{ai}.txt（或 公共.txt / 首个 .txt），无则生成默认提示；注入上游产物。"""
    instr = None
    if cmd_dir and os.path.isdir(cmd_dir):
        fp = os.path.join(cmd_dir, ai + ".txt")
        if not os.path.exists(fp):
            fp = os.path.join(cmd_dir, "公共.txt")
        if not os.path.exists(fp):
            fs = [f for f in os.listdir(cmd_dir) if f.endswith(".txt")]
            if fs:
                fp = os.path.join(cmd_dir, fs[0])
        if os.path.exists(fp):
            instr = open(fp, encoding="utf-8").read()
    if not instr:
        base = f"【写作环节：{link.get('name', '')}】"
        if upstream and upstream.strip():
            return base + "\n请基于以下上游环节产物进行本环节创作（不要照抄）：\n" + upstream
        return base + "\n（请在指令目录放置本环节任务说明，或在此补充要求。）"
    if upstream and upstream.strip():
        return ("【上游环节产物（参考素材，勿照抄）】\n" + upstream +
                "\n\n==== 本环节任务指令 ====\n" + instr)
    return instr


def _run_assigned(s, log_fn):
    """环节→AI 指派执行：只发 assigned 列表 AI；race=各出一份，serial=依次接力注入。"""
    # 新模型（固定 5 环节）的桥接 link 标记 _legacy_proxy：交给新执行器，跳过旧分支。
    if s.get("_legacy_proxy"):
        log_fn("⚠ 该环节为固定 5 环节桥接代理，已交由新执行器处理，旧分支跳过。")
        return 0, 0
    assigned = s.get("assigned") or []
    if not assigned:
        log_fn("⚠ 该环节未指派 AI，跳过")
        return 0, 0
    mode = s.get("mode", "single")
    inject = s.get("inject", False)
    up_txt = upstream_text(s) if inject else ""
    cmd_dir = os.path.join(COLLAB_ROOT, s.get("cmd_dir", "")) if s.get("cmd_dir") else None
    need = s.get("need", 1)

    def _done(ai):
        d = artifact_dir(ai, s)
        return os.path.isdir(d) and len(
            [f for f in os.listdir(d) if f.endswith((".md", ".json"))]) >= need

    if mode == "serial":
        prev = up_txt
        ok = 0
        for ai in assigned:
            if _done(ai):
                log_fn(f"  ✅ {ai} 已达标，跳过")
                ok += 1
            else:
                text = _build_prompt(cmd_dir, ai, s, prev)
                log_fn(f"→ {ai}（串行·带上游 {len(prev)}字）")
                if _send_assigned(ai, text, log_fn, s):
                    ok += 1
            art = latest_artifact(ai, s)
            if art:
                prev = art
            time.sleep(3)
        return ok, len(assigned)

    # race / single：所有指派 AI 各自独立，仅注入本环节上游
    ok = 0
    for ai in assigned:
        if _done(ai):
            log_fn(f"  ✅ {ai} 已达标，跳过")
            ok += 1
            continue
        text = _build_prompt(cmd_dir, ai, s, up_txt)
        label = "赛马" if mode == "race" else "单写"
        log_fn(f"→ {ai}（{label}·上游 {len(up_txt)}字）")
        if _send_assigned(ai, text, log_fn, s):
            ok += 1
        time.sleep(3)
    return ok, len(assigned)


def rerun_stage(stage_key, log_fn):
    """重跑单个阶段：复用 execute_stage 的 action 分支（只发未达标家，幂等安全），不改动 STAGES。"""
    s = KEY2STAGE.get(stage_key)
    if not s:
        log_fn(f"❌ 未知阶段: {stage_key}")
        return 0, 0
    log_fn(f"🔄 重跑阶段：{s['name']}")
    return execute_stage(stage_key, log_fn)
