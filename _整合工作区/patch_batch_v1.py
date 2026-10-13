import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_do_produce_batch" in text:
    print("[SKIP] 补丁已存在")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_batch_v1")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

FUNC_BLOCK = r'''


# ═══════════════════════════════════════════════════════════════════════
# 批量多文件产出引擎 + 重试兜底
# ═══════════════════════════════════════════════════════════════════════

# ── 重试参数（已在设计阶段确认）──
RETRY_T_FIRST      = 200    # 首轮等待（秒）
RETRY_T_BUSY_LOOP  = 100    # AI 忙时再等（秒）
RETRY_T_RETRY      = 200    # 重试等待（秒）
RETRY_MAX_ATTEMPTS = 3      # 单 AI 最多尝试次数（首轮 + 2 次重试）


def _read_expected_files(phase_cfg, out_dir, chunk_id=None):
    """读本环节期望产出的文件清单。
    返回 [(item_key, item_data), ...]（按 split.json 的列表）。
    """
    spec = _get_split_spec(phase_cfg, out_dir, chunk_id)
    if not spec:
        return []
    items = spec.get("列表") or []
    return [(it.get("key") or it.get("name") or f"item{i}", it)
            for i, it in enumerate(items, 1)]


def _build_batch_prompt(phase_cfg, expected, out_dir, ai_key):
    """构造"生成 N 个文件"的 prompt，附完整文件清单。
    返回 (清单文本, [(item_key, out_path), ...])
    """
    lines = [f"【本环节需生成的完整文件清单（共 {len(expected)} 个，一个都不能漏）】"]
    paths = []
    versions_dir = Path(out_dir) / "versions"
    for item_key, item_data in expected:
        safe = str(item_key).replace("/", "_").replace("\\", "_").replace(":", "_").strip()[:40]
        out_path = versions_dir / f"{ai_key}__{safe}.md"
        paths.append((item_key, out_path))
        lines.append(f"  · {item_key}   →   {out_path}")
    lines.append("")
    lines.append("【完成判定】")
    lines.append(f"  - 必须生成上面清单里全部 {len(expected)} 个文件")
    lines.append(f"  - 每个文件 ≥ 200 字")
    lines.append(f"  - 文件不存在或不完整 = 任务失败")
    return "\n".join(lines), paths


def _write_failed_record(project_root, phase_key, stage, attempts, task_preview):
    """写失败记录到 <project>/_failed/<phase_key>/<stage>.json。"""
    import json as _json
    failed_dir = Path(project_root) / "_failed"
    phase_dir = failed_dir / phase_key
    phase_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "phase_key": phase_key,
        "stage": stage,
        "attempts": attempts,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "task_preview": task_preview[:300],
        "status": "pending",
    }
    (phase_dir / f"{stage}.json").write_text(
        _json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 更新 _index.json
    index_path = failed_dir / "_index.json"
    index = {"by_phase": {}, "updated": record["timestamp"]}
    if index_path.exists():
        try:
            index = _json.loads(index_path.read_text(encoding="utf-8"))
            index["updated"] = record["timestamp"]
        except Exception:
            pass
    plist = index.setdefault("by_phase", {}).setdefault(phase_key, [])
    if stage not in plist:
        plist.append(stage)
    index["total"] = sum(len(v) for v in index["by_phase"].values())
    index_path.write_text(
        _json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"   ⛔ 已写失败记录：{phase_dir / (stage + '.json')}")


def _judge_task_status(ai_key, verify_fn, wait_sec):
    """等待 wait_sec，每 5s 检查一次。
    返回 'success' / 'busy' / 'idle_no_output'
    """
    try:
        from mix_send import is_ai_busy
    except Exception:
        time.sleep(wait_sec)
        ok, _ = verify_fn()
        return "success" if ok else "idle_no_output"

    t0 = time.time()
    while time.time() - t0 < wait_sec:
        ok, _ = verify_fn()
        if ok:
            return "success"
        if not is_ai_busy(ai_key):
            time.sleep(5)
            ok, _ = verify_fn()
            if ok:
                return "success"
            if not is_ai_busy(ai_key):
                return "idle_no_output"
        time.sleep(5)

    return "busy" if is_ai_busy(ai_key) else "idle_no_output"


def _send_batch_task(ai_key, task_text, dry=False):
    """发送任务到指定 AI。返回 True/False。"""
    if dry:
        return True
    try:
        from mix_send import send
        r = send(ai_key, task_text)
        rs = str(r or "").lstrip()
        if rs.startswith("✅"):
            print(f"   [{ai_key}] 任务已发送")
            return True
        print(f"   [{ai_key}] 发送返回异常：{rs[:80]}")
        return False
    except Exception as e:
        print(f"   [{ai_key}] 发送失败：{e}")
        return False


def _run_with_retry_fallback(
    phase_cfg, out_dir, primary_ai, backup_ais,
    task_text_builder,      # 函数：(ai_key) → task_text
    verify_fn,              # 函数：() → (ok, detail)
    dry=False,
):
    """任务级重试 + 兜底。
    - primary_ai 先跑 3 次
    - 失败 → 依次试 backup_ais（各 3 次）
    - 全部失败 → 写 _failed/ 记录，返回 False
    """
    ai_order = [primary_ai] + list(backup_ais or [])
    attempts_log = []
    phase_key = f"{_STAGE_DIR_MAP.get('写作', '写作')}__{phase_cfg.get('name') or phase_cfg.get('key')}"
    project_root = _project_root()

    for ai_idx, ai_key in enumerate(ai_order):
        ai_attempts = {"ai": ai_key, "count": 0, "last_error": ""}
        is_primary = (ai_idx == 0)
        print(f"\n   ── [{ai_key}] {'主' if is_primary else '兜底'} AI 开始 ──")

        for attempt in range(RETRY_MAX_ATTEMPTS):
            t_wait = RETRY_T_FIRST if attempt == 0 else RETRY_T_RETRY

            # 等空闲
            if not dry:
                try:
                    from mix_send import wait_idle
                    if not wait_idle(ai_key, timeout=300, poll=5):
                        print(f"   [{ai_key}] 等空闲超时，换下一个 AI")
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception as e:
                    print(f"   [{ai_key}] wait_idle 异常：{e}")

            # 发送
            print(f"   [{ai_key}] 第 {attempt+1}/{RETRY_MAX_ATTEMPTS} 次（等 {t_wait}s）")
            task_text = task_text_builder(ai_key)
            if not _send_batch_task(ai_key, task_text, dry):
                ai_attempts["count"] += 1
                ai_attempts["last_error"] = "send_failed"
                continue

            # 判定
            status = _judge_task_status(ai_key, verify_fn, t_wait) if not dry else "success"
            if status == "success":
                print(f"   [{ai_key}] ✓ 成功")
                return True
            if status == "busy":
                print(f"   [{ai_key}] AI 仍在忙，再等 {RETRY_T_BUSY_LOOP}s")
                time.sleep(RETRY_T_BUSY_LOOP)
                ok, _ = verify_fn()
                if ok:
                    print(f"   [{ai_key}] ✓ 补等后成功")
                    return True
            ai_attempts["count"] += 1
            ai_attempts["last_error"] = status

        attempts_log.append(ai_attempts)

    # 全部失败
    _write_failed_record(project_root, phase_key, "产出",
                          attempts_log, task_text_builder(primary_ai)[:300])
    print(f"\n   ⛔ [{phase_key}] 产出阶段全 AI 失败，已写 _failed/ 记录")
    return False


def _do_produce_batch(
    agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
    input_text, out_dir, dry, extra_note, ai_assist, split_spec,
):
    """批量产出：1 条命令让 AI 生成 N 个文件。
    成功返回 [(item_key, out_path), ...]；失败返回 []。
    """
    expected = [(it.get("key") or it.get("name") or f"item{i}", it)
                for i, it in enumerate(split_spec.get("列表") or [], 1)]
    if not expected:
        return []

    # 构造 4 个 AI 的兜底顺序（排除当前主 AI）
    _all_parts = sess.get("participants") or []
    primary_key = app["key"]
    backup_keys = [p["key"] for p in _all_parts if p["key"] != primary_key]

    # 期望文件清单（占位，仅用于校验）
    _versions_dir = Path(out_dir) / "versions"
    _versions_dir.mkdir(parents=True, exist_ok=True)

    # ── verify_fn：检查所有文件是否都达标 ──
    def verify_fn(ai_key_override=None):
        # 因为兜底时 ai_key 会变，需要动态计算路径
        _ai = ai_key_override or primary_key
        missing = 0
        for item_key, _ in expected:
            safe = str(item_key).replace("/", "_").replace("\\", "_").replace(":", "_").strip()[:40]
            p = _versions_dir / f"{_ai}__{safe}.md"
            if not (p.exists() and p.stat().st_size >= 100):
                missing += 1
        total = len(expected)
        ok = (missing == 0)
        return ok, f"{total - missing}/{total}"

    # ── task_text_builder ──
    def build_task(ai_key):
        files_text, _paths = _build_batch_prompt(phase_cfg, expected, out_dir, ai_key)
        full = (input_text + "\n\n" + files_text).replace("<你的名字>", ai_key)
        return full

    # ── 调用重试兜底 ──
    # 因为 verify_fn 需要感知当前 ai_key，闭包捕获有问题，改用重试内联
    # 简化：先对每个 AI 尝试；每个 AI 内部重试

    ai_order = [primary_key] + backup_keys
    attempts_log = []
    phase_key = f"{_STAGE_DIR_MAP.get(program, program)}__{phase_cfg.get('name') or phase_cfg.get('key')}"
    project_root = _project_root()

    for ai_idx, ai_key in enumerate(ai_order):
        ai_attempts = {"ai": ai_key, "count": 0, "last_error": ""}
        print(f"\n   ── [{ai_key}] {'主' if ai_idx == 0 else '兜底'} AI 开始 ──")

        for attempt in range(RETRY_MAX_ATTEMPTS):
            t_wait = RETRY_T_FIRST if attempt == 0 else RETRY_T_RETRY

            if not dry:
                try:
                    from mix_send import wait_idle
                    if not wait_idle(ai_key, timeout=300, poll=5):
                        print(f"   [{ai_key}] 等空闲超时")
                        ai_attempts["last_error"] = "wait_idle_timeout"
                        break
                except Exception:
                    pass

            print(f"   [{ai_key}] 第 {attempt+1}/{RETRY_MAX_ATTEMPTS} 次（等 {t_wait}s）")
            task_text = build_task(ai_key)
            if not _send_batch_task(ai_key, task_text, dry):
                ai_attempts["count"] += 1
                ai_attempts["last_error"] = "send_failed"
                continue

            # 闭包传入当前 ai_key
            def _vf(_k=ai_key):
                return verify_fn(_k)

            status = _judge_task_status(ai_key, _vf, t_wait) if not dry else "success"
            if status == "success":
                print(f"   [{ai_key}] ✓ 成功")
                # 返回实际产出的文件
                out_files = []
                for item_key, _ in expected:
                    safe = str(item_key).replace("/", "_").replace("\\", "_").replace(":", "_").strip()[:40]
                    p = _versions_dir / f"{ai_key}__{safe}.md"
                    out_files.append(p)
                return out_files
            if status == "busy":
                print(f"   [{ai_key}] AI 仍在忙，再等 {RETRY_T_BUSY_LOOP}s")
                time.sleep(RETRY_T_BUSY_LOOP)
                ok, _ = _vf()
                if ok:
                    out_files = []
                    for item_key, _ in expected:
                        safe = str(item_key).replace("/", "_").replace("\\", "_").replace(":", "_").strip()[:40]
                        p = _versions_dir / f"{ai_key}__{safe}.md"
                        out_files.append(p)
                    return out_files
            ai_attempts["count"] += 1
            ai_attempts["last_error"] = status

        attempts_log.append(ai_attempts)

    # 全部失败
    _write_failed_record(project_root, phase_key, "产出",
                          attempts_log, build_task(primary_key)[:300])
    print(f"\n   ⛔ [{phase_key}] 产出阶段全 AI 失败，已写 _failed/")
    return []
'''

# 插入到 __main__ 之前
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
print(f"     新文件大小：{len(new_text)} 字符")
