import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_all_batch")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

changed = 0

# ══════════════════════════════════════════════════════════════
# 补丁 1：run_mesh_phase 的批量短路，对所有非人物设计环节生效
# ══════════════════════════════════════════════════════════════
OLD1 = '''    # ── 批量模式短路：拆分环节或生产者环节，都走 产出→盲审→拼接 一体化 ──
    _batch_split_spec = None
    _phase_name_now = phase_cfg.get("name") or phase_cfg.get("key") or ""

    # 情况 A：生产者环节（产出 1 份 md + 1 份 split.json，放各自 AI 目录）
    if _phase_name_now in SPLIT_PRODUCERS:
        _batch_split_spec = {
            "拆分维度": "单件",
            "列表": [{"key": _phase_name_now, "name": _phase_name_now,
                       "start": 0, "end": 0, "note": "整个环节一份产出"}]
        }
    else:
        # 情况 B：消费者环节（读上游 split.json）
        for _cid_b, _, _ in chunks:
            _sp = _get_split_spec(phase_cfg, out_dir, _cid_b)
            if _sp and _sp.get("列表"):
                _batch_split_spec = _sp
                break

    if _batch_split_spec is not None:
        return _run_batch_mesh(
            agent, sess, cfg, program, phase_cfg, chapter,
            input_text, out_dir, dry,
            writers=phase_writers,
            reviewers=phase_reviewers,
            merger=phase_merger,
            split_spec=_batch_split_spec,
        )'''

NEW1 = '''    # ── 批量模式短路：所有 mesh 环节统一走 产出→盲审→拼接，目录隔离 ──
    _phase_name_now = phase_cfg.get("name") or phase_cfg.get("key") or ""

    # 人物设计特殊处理（走它自己的多人多文件逻辑）
    if "人物设计" not in _phase_name_now:
        _batch_split_spec = None

        # 优先读上游 split.json（消费者）
        for _cid_b, _, _ in chunks:
            _sp = _get_split_spec(phase_cfg, out_dir, _cid_b)
            if _sp and _sp.get("列表"):
                _batch_split_spec = _sp
                break

        # 无上游 split.json → 单件模式（生产者 / 独立环节）
        if _batch_split_spec is None:
            _batch_split_spec = {
                "拆分维度": "单件",
                "列表": [{"key": _phase_name_now, "name": _phase_name_now,
                           "start": 0, "end": 0, "note": "整个环节一份产出"}]
            }

        return _run_batch_mesh(
            agent, sess, cfg, program, phase_cfg, chapter,
            input_text, out_dir, dry,
            writers=phase_writers,
            reviewers=phase_reviewers,
            merger=phase_merger,
            split_spec=_batch_split_spec,
        )'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 补丁1：所有非人物设计环节统一走批量")
    changed += 1
else:
    print("[FAIL] 补丁1 找不到锚点")

# ══════════════════════════════════════════════════════════════
# 补丁 2：旧 do_produce 也改目录隔离（防御性，防直接调用）
# ══════════════════════════════════════════════════════════════
OLD2 = '''    out = Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"
    out.parent.mkdir(parents=True, exist_ok=True)   # 保证 versions 目录存在
    label = f"{program} › {phase_cfg['key']}"'''

NEW2 = '''    # 目录隔离：versions/<ai>/<chunk>.md
    _ai_dir = Path(out_dir) / "versions" / app["key"]
    _ai_dir.mkdir(parents=True, exist_ok=True)
    out = _ai_dir / f"{chunk_id}.md"
    label = f"{program} › {phase_cfg['key']}"'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 补丁2：do_produce 改目录隔离")
    changed += 1
else:
    print("[WARN] 补丁2 找不到锚点（可能已改）")

# ══════════════════════════════════════════════════════════════
# 补丁 3：旧 _do_produce_split 改目录隔离
# ══════════════════════════════════════════════════════════════
OLD3 = '''    _versions_dir = Path(out_dir) / "versions"
    _versions_dir.mkdir(parents=True, exist_ok=True)

    _tpl = compose_prompt("PROMPT_PRODUCE.md", program)
    _base_note = format_note(program, phase_cfg) or ""
    if extra_note:
        _base_note = (_base_note + "\\n\\n【上一轮终审反对意见（必须逐条对应处理）】\\n" + extra_note).strip()

    _phase_name = phase_cfg.get("key") or phase_cfg.get("name") or ""
    _produced = []

    for _idx, item in enumerate(items, start=1):
        _key = item.get("key") or item.get("任务名") or item.get("name") or f"item{_idx}"
        _safe = _key.replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
        _out = _versions_dir / f"{chunk_id}__{app['key']}__{_safe}.md"'''

NEW3 = '''    _ai_dir = Path(out_dir) / "versions" / app["key"]
    _ai_dir.mkdir(parents=True, exist_ok=True)

    _tpl = compose_prompt("PROMPT_PRODUCE.md", program)
    _base_note = format_note(program, phase_cfg) or ""
    if extra_note:
        _base_note = (_base_note + "\\n\\n【上一轮终审反对意见（必须逐条对应处理）】\\n" + extra_note).strip()

    _phase_name = phase_cfg.get("key") or phase_cfg.get("name") or ""
    _produced = []

    for _idx, item in enumerate(items, start=1):
        _key = item.get("key") or item.get("任务名") or item.get("name") or f"item{_idx}"
        _safe = _key.replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
        _out = _ai_dir / f"{_safe}.md"'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 补丁3：_do_produce_split 改目录隔离")
    changed += 1
else:
    print("[WARN] 补丁3 找不到锚点")

# ══════════════════════════════════════════════════════════════
# 补丁 4：旧 do_review 改目录隔离
# ══════════════════════════════════════════════════════════════
OLD4 = '''    out = Path(out_dir) / "reviews" / f"{chunk_id}__{Path(target_path).stem}__{app['key']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)   # 保证 reviews 目录存在'''

NEW4 = '''    # 目录隔离：reviews/<ai>/<target>.json
    _review_dir = Path(out_dir) / "reviews" / app["key"]
    _review_dir.mkdir(parents=True, exist_ok=True)
    out = _review_dir / f"{Path(target_path).stem}.json"'''

if OLD4 in text:
    text = text.replace(OLD4, NEW4, 1)
    print("[OK] 补丁4：do_review 改目录隔离")
    changed += 1
else:
    print("[WARN] 补丁4 找不到锚点")

# ══════════════════════════════════════════════════════════════
# 补丁 5：dry-run 伪造路径也改目录式
# ══════════════════════════════════════════════════════════════
OLD5 = '''            else:
                versions = [Path(out_dir) / "versions" / f"{cid}__{w['key']}.md" for w in writers]'''

NEW5 = '''            else:
                # 单件模式：versions/<ai>/<cid>.md
                versions = [Path(out_dir) / "versions" / w["key"] / f"{cid}.md" for w in writers]'''

if OLD5 in text:
    text = text.replace(OLD5, NEW5, 1)
    print("[OK] 补丁5：dry-run 伪造路径改目录式")
    changed += 1
else:
    print("[WARN] 补丁5 找不到锚点")

# 写回
if changed >= 3:
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回（{changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处，未写回")
