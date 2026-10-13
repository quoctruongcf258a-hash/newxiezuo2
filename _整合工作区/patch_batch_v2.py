import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_do_review_batch" in text and "_do_merge_batch" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_batch_v2")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

FUNC_BLOCK = r'''


# 
# 通用阶段重试 + 批量盲审 + 批量拼接
# 

def _run_task_stage(
    primary_ai_key, backup_ai_keys, task_builder, verify_fn,
    phase_key, stage, dry=False,
):
    """跑一个阶段任务（产出/盲审/拼接/修改），带重试+兜底。
    返回 (success: bool, final_ai_key: str or None)
    """
    ai_order = [primary_ai_key] + list(backup_ai_keys or [])
    attempts_log = []
    project_root = _project_root()

    for ai_idx, ai_key in enumerate(ai_order):
        ai_attempts = {"ai": ai_key, "count": 0, "last_error": ""}
        print(f"    [{ai_key}] {'主' if ai_idx == 0 else '兜底'} AI 开始 ")

        for attempt in range(RETRY_MAX_ATTEMPTS):
            t_wait = RETRY_T_FIRST if attempt == 0 else RETRY_T_RETRY

            if not dry:
                try:
                    from mix_send import wait_idle
                    if not wait_idle(ai_key, timeout=300, poll=5):
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception:
                    pass

            print(f"   [{ai_key}] 第 {attempt+1}/{RETRY_MAX_ATTEMPTS} 次（等 {t_wait}s）")
            task_text = task_builder(ai_key)
            if not _send_batch_task(ai_key, task_text, dry):
                ai_attempts["count"] += 1
                ai_attempts["last_error"] = "send_failed"
                continue

            def _vf(_k=ai_key):
                return verify_fn(_k)

            status = _judge_task_status(ai_key, _vf, t_wait) if not dry else "success"
            if status == "success":
                print(f"   [{ai_key}] ✓ 成功")
                return True, ai_key
            if status == "busy":
                print(f"   [{ai_key}] AI 仍在忙，再等 {RETRY_T_BUSY_LOOP}s")
                time.sleep(RETRY_T_BUSY_LOOP)
                ok, _ = _vf()
                if ok:
                    return True, ai_key
            ai_attempts["count"] += 1
            ai_attempts["last_error"] = status

        attempts_log.append(ai_attempts)

    _write_failed_record(project_root, phase_key, stage,
                          attempts_log, task_builder(primary_ai_key)[:300])
    print(f"\n   ⛔ [{phase_key}] {stage} 阶段全 AI 失败，已写 _failed/")
    return False, None


def _do_review_batch(agent, sess, phase_cfg, reviewer_app, out_dir, dry=False):
    """批量盲审：让 reviewer 读其他 AI 的产出文件夹，输出一份综合审核报告。
    返回审核报告路径 或 None。
    """
    reviewer_key = reviewer_app["key"]
    review_dir = Path(out_dir) / "reviews" / reviewer_key
    review_dir.mkdir(parents=True, exist_ok=True)
    report_file = review_dir / "审核报告.md"

    versions_dir = Path(out_dir) / "versions"
    if not versions_dir.exists():
        return None
    all_ai_dirs = [d for d in versions_dir.iterdir() if d.is_dir()]
    read_dirs = [d for d in all_ai_dirs if d.name != reviewer_key]

    if not read_dirs:
        print(f"   [{reviewer_key}] 没有其他 AI 的产出可审，跳过")
        return None

    read_list = "\n".join(f"   {d}" for d in read_dirs)

    def build_task(ai_key):
        return f"""【任务：盲审】

请读取以下文件夹里的全部文件（每个文件夹是一个 AI 的产出）：
{read_list}

【做什么】
对这些文件逐章进行横向对比审核，每个章节都要覆盖到，输出一份综合审核报告：

对每一章：
  1. 对比多个版本，指出每个版本的优点和缺点
  2. 推荐哪个版本最佳（或指出各版本可取之处）
  3. 给出具体可执行的修改建议（不要空话）

【输出要求】
- 把完整审核报告一次性保存到：
    {report_file}
- 报告格式：每章一节，节内按"版本对比 / 推荐 / 修改建议"三段
- 只输出报告正文，不要多余的对话式说明
"""

    def verify_fn(ai_key):
        ok = report_file.exists() and report_file.stat().st_size >= 100
        size = report_file.stat().st_size if report_file.exists() else 0
        return ok, f"{size} 字"

    all_keys = [p["key"] for p in (sess.get("participants") or [])]
    backup_keys = [k for k in all_keys if k != reviewer_key]

    ok, final_ai = _run_task_stage(
        primary_ai_key=reviewer_key,
        backup_ai_keys=backup_keys,
        task_builder=build_task,
        verify_fn=verify_fn,
        phase_key=f"reviews__{phase_cfg.get('name') or phase_cfg.get('key')}",
        stage="盲审",
        dry=dry,
    )
    if final_ai and final_ai != reviewer_key:
        print(f"   [盲审] {reviewer_key} 失败  {final_ai} 代审完成")
    return report_file if ok else None


def _do_merge_batch(agent, sess, phase_cfg, merger_app, out_dir, dry=False):
    """批量拼接：让 merger 读所有 AI 的产出 + 审核报告，输出融合稿。"""
    merger_key = merger_app["key"]
    merged_dir = Path(out_dir) / "merged"
    merged_dir.mkdir(parents=True, exist_ok=True)
    merged_file = merged_dir / "融合稿.md"

    versions_dir = Path(out_dir) / "versions"
    reviews_dir = Path(out_dir) / "reviews"

    def build_task(ai_key):
        return f"""【任务：融合】

请读取以下文件夹里的全部文件：
- 所有 AI 的产出：{versions_dir}/
- 所有 AI 的审核报告：{reviews_dir}/

【做什么】
对每一章：
  1. 对比所有 AI 版本的优缺点（参考审核报告）
  2. 挑选最优版本，或融合各版本优点形成更优版本
  3. 输出该章的最终版

【输出要求】
- 把所有章节的最终版按章顺序合成一份文件，保存到：
    {merged_file}
- 每章标题格式：# 第N章 <标题>
- 不要输出解释、不要输出对照表
"""

    def verify_fn(ai_key):
        ok = merged_file.exists() and merged_file.stat().st_size >= 200
        size = merged_file.stat().st_size if merged_file.exists() else 0
        return ok, f"{size} 字"

    all_keys = [p["key"] for p in (sess.get("participants") or [])]
    backup_keys = [k for k in all_keys if k != merger_key]

    ok, final_ai = _run_task_stage(
        primary_ai_key=merger_key,
        backup_ai_keys=backup_keys,
        task_builder=build_task,
        verify_fn=verify_fn,
        phase_key=f"merge__{phase_cfg.get('name') or phase_cfg.get('key')}",
        stage="拼接",
        dry=dry,
    )
    if final_ai and final_ai != merger_key:
        print(f"   [拼接] {merger_key} 失败  {final_ai} 代拼完成")
    return merged_file if ok else None


def _do_modify_single(agent, sess, phase_cfg, writer_app, out_dir, dry=False):
    """单 AI 模式：让该 AI 读自己的产出 + 自审报告，输出修改版。"""
    writer_key = writer_app["key"]
    merged_dir = Path(out_dir) / "merged"
    merged_dir.mkdir(parents=True, exist_ok=True)
    merged_file = merged_dir / "最终版.md"

    versions_dir = Path(out_dir) / "versions" / writer_key
    review_file = Path(out_dir) / "reviews" / writer_key / "审核报告.md"

    def build_task(ai_key):
        return f"""【任务：根据自审报告修改】

请读取：
- 你的产出：{versions_dir}/
- 你的自审报告：{review_file}

【做什么】
1. 逐条对照自审报告里的修改建议
2. 输出修改后的最终版

【输出要求】
- 把所有章节的最终版按章顺序合成一份文件，保存到：
    {merged_file}
- 每章标题格式：# 第N章 <标题>
- 不要输出解释
"""

    def verify_fn(ai_key):
        ok = merged_file.exists() and merged_file.stat().st_size >= 200
        size = merged_file.stat().st_size if merged_file.exists() else 0
        return ok, f"{size} 字"

    all_keys = [p["key"] for p in (sess.get("participants") or [])]
    backup_keys = [k for k in all_keys if k != writer_key]

    ok, _ = _run_task_stage(
        primary_ai_key=writer_key,
        backup_ai_keys=backup_keys,
        task_builder=build_task,
        verify_fn=verify_fn,
        phase_key=f"modify__{phase_cfg.get('name') or phase_cfg.get('key')}",
        stage="修改",
        dry=dry,
    )
    return merged_file if ok else None


def _run_batch_mesh(
    agent, sess, cfg, program, phase_cfg, chapter,
    input_text, out_dir, dry,
    writers, reviewers, merger, split_spec,
):
    """批量模式下跑整个环节：产出  盲审  拼接（多AI）/ 修改（单AI）。"""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    versions_dir = Path(out_dir) / "versions"

    #  阶段1：产出 
    print(f"\n{'='*70}\n【阶段1：产出】{len(writers)} 个 AI 并发\n{'='*70}")
    all_versions = {}

    if not dry and len(writers) > 1:
        with ThreadPoolExecutor(max_workers=len(writers)) as _ex:
            _futs = {}
            def _produce_locked(_w):
                with _get_ai_lock(_w["key"]):
                    return do_produce(agent, sess, _w, program, phase_cfg,
                                       "batch", phase_cfg.get("key") or "",
                                       input_text, out_dir, dry,
                                       ai_assist=False)
            for w in writers:
                _futs[_ex.submit(_produce_locked, w)] = w
            for _fut in as_completed(_futs):
                w = _futs[_fut]
                try:
                    v = _fut.result()
                    if isinstance(v, list):
                        all_versions[w["key"]] = v
                        print(f"   ✓ {w['key']} 完成：{len(v)} 个文件")
                    else:
                        print(f"   ✗ {w['key']} 无产出")
                except Exception as e:
                    print(f"   ✗ {w['key']} 异常：{e}")
    else:
        for w in writers:
            try:
                v = do_produce(agent, sess, w, program, phase_cfg,
                                "batch", phase_cfg.get("key") or "",
                                input_text, out_dir, dry,
                                ai_assist=False)
                if isinstance(v, list):
                    all_versions[w["key"]] = v
                    print(f"   ✓ {w['key']} 完成：{len(v)} 个文件")
            except Exception as e:
                print(f"   ✗ {w['key']} 异常：{e}")

    _missing_w = [w["key"] for w in writers if w["key"] not in all_versions]
    if _missing_w:
        print(f"   ⛔ 产出未完成：{_missing_w}")
        return None

    #  阶段2：盲审 
    print(f"\n{'='*70}\n【阶段2：盲审】{len(reviewers)} 个 AI 并发\n{'='*70}")
    all_reviews = {}

    if not dry and len(reviewers) > 1:
        with ThreadPoolExecutor(max_workers=len(reviewers)) as _ex:
            _futs = {}
            def _review_locked(_r):
                with _get_ai_lock(_r["key"]):
                    return _do_review_batch(agent, sess, phase_cfg, _r, out_dir, dry)
            for r in reviewers:
                _futs[_ex.submit(_review_locked, r)] = r
            for _fut in as_completed(_futs):
                r = _futs[_fut]
                try:
                    rv = _fut.result()
                    if rv:
                        all_reviews[r["key"]] = rv
                        print(f"   ✓ {r['key']} 审完")
                except Exception as e:
                    print(f"   ✗ {r['key']} 异常：{e}")
    else:
        for r in reviewers:
            rv = _do_review_batch(agent, sess, phase_cfg, r, out_dir, dry)
            if rv:
                all_reviews[r["key"]] = rv
                print(f"   ✓ {r['key']} 审完")

    _missing_r = [r["key"] for r in reviewers if r["key"] not in all_reviews]
    if _missing_r:
        print(f"   ⛔ 盲审未完成：{_missing_r}")
        return None

    #  阶段3：拼接（多AI）或 修改（单AI）
    if len(writers) >= 2:
        print(f"\n{'='*70}\n【阶段3：拼接】\n{'='*70}")
        return _do_merge_batch(agent, sess, phase_cfg, merger, out_dir, dry)
    else:
        print(f"\n{'='*70}\n【阶段3：修改】单 AI 自审+修改\n{'='*70}")
        return _do_modify_single(agent, sess, phase_cfg, writers[0], out_dir, dry)
'''

anchor = '\nif __name__ == "__main__":'
i_main = text.find(anchor)
if i_main < 0:
    print("[FAIL] 找不到 __main__ 锚点")
    raise SystemExit(1)

before = text[:i_main].rstrip()
after = text[i_main:]
new_text = before + "\n\n\n" + FUNC_BLOCK.strip() + "\n\n" + after.lstrip("\n")
TARGET.write_text(new_text, encoding="utf-8")
print(f"[OK] 已写入 {len(FUNC_BLOCK)} 字符的新函数块")
