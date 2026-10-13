import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "SPLIT_PRODUCERS" in text and "_do_produce_split" in text:
    print("[SKIP] 已打过补丁")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_split_engine")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

changed = 0

# ── 补丁 A：在 def format_note 前插入常量 ──
OLD_A = 'def format_note(program, phase_cfg) -> str:'
NEW_A = '''# ── 拆分映射表 ──
SPLIT_PRODUCERS = {
    "全书结构": "卷",
    "分卷结构": "季",
    "粗纲规划": "章",
}
SPLIT_SOURCES = {
    "分卷结构": "全书结构",
    "情绪规划": "全书结构",
    "粗纲规划": "分卷结构",
    "简短细纲规划": "粗纲规划",
    "详细细纲规划": "粗纲规划",
    "前30章章纲": "粗纲规划",
}


def format_note(program, phase_cfg) -> str:'''

if OLD_A in text and "SPLIT_PRODUCERS" not in text:
    text = text.replace(OLD_A, NEW_A, 1)
    print("[OK] A：插入 SPLIT_PRODUCERS / SPLIT_SOURCES")
    changed += 1
else:
    print("[FAIL] A")

# ── 补丁 B：format_note fields 分支追加 split hint ──
OLD_B = '''        if _fields:
            _lines = "\\n".join(f"  {f}：" for f in _fields)
            return ("严格按下面字段输出，一行一个字段，不要增减：\\n"
                    + _lines
                    + "\\n  （补充说明：如本环节有其他必要信息，可在最后另起一节）")'''

NEW_B = '''        if _fields:
            _lines = "\\n".join(f"  {f}：" for f in _fields)
            _base = ("严格按下面字段输出，一行一个字段，不要增减：\\n"
                    + _lines
                    + "\\n  （补充说明：如本环节有其他必要信息，可在最后另起一节）")
            _pn = phase_cfg.get("name") or phase_cfg.get("key") or ""
            if _pn in SPLIT_PRODUCERS:
                _dim = SPLIT_PRODUCERS[_pn]
                _base += (
                    "\\n\\n【额外要求：结构化清单】\\n"
                    "在上面正文的最后，追加一个 JSON 代码块（用三反引号 json 和三反引号 包裹），\\n"
                    "用于下游环节自动拆分任务。JSON 必须符合下面格式：\\n\\n"
                    "json\\n"
                    "{\\n"
                    '  "拆分维度": "' + _dim + '",\\n'
                    '  "列表": [\\n'
                    '    {"key": "' + _dim + '1", "name": "名称", "start": 1, "end": 50, "note": "要点"}\\n'
                    "  ]\\n"
                    "}\\n"
                    "\\n\\n"
                    "要求：\\n"
                    "- 列表里的每一项代表一个下游任务单元\\n"
                    '- key 用短标识（如 "' + _dim + '1"）\\n'
                    "- 必须覆盖整个" + _dim + "范围，不能遗漏\\n"
                    "- JSON 必须语法合法，不能有注释\\n"
                )
            return _base'''

if OLD_B in text:
    text = text.replace(OLD_B, NEW_B, 1)
    print("[OK] B：format_note 追加 split hint")
    changed += 1
else:
    print("[FAIL] B")

# ── 补丁 C：do_produce 顶部加通用拆分拦截 ──
OLD_C = '''    # ── 人物设计：每个人物单独调 AI，各自落一个文件 ──
    _pkey = phase_cfg.get("key") or phase_cfg.get("name") or ""
    if "人物设计" in _pkey:
        return _do_produce_renwu(
            agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
            input_text, out_dir, dry, extra_note=extra_note, ai_assist=ai_assist
        )
    out = Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"'''

NEW_C = '''    # ── 人物设计：每个人物单独调 AI，各自落一个文件 ──
    _pkey = phase_cfg.get("key") or phase_cfg.get("name") or ""
    if "人物设计" in _pkey:
        return _do_produce_renwu(
            agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
            input_text, out_dir, dry, extra_note=extra_note, ai_assist=ai_assist
        )
    # ── 通用拆分：按上游 split.json 循环调 AI ──
    _split_spec = _get_split_spec(phase_cfg, out_dir)
    if _split_spec and _split_spec.get("列表"):
        return _do_produce_split(
            agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
            input_text, out_dir, dry, extra_note=extra_note,
            ai_assist=ai_assist, split_spec=_split_spec
        )
    out = Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"'''

if OLD_C in text:
    text = text.replace(OLD_C, NEW_C, 1)
    print("[OK] C：do_produce 顶部加通用拆分拦截")
    changed += 1
else:
    print("[FAIL] C")

# ── 补丁 D：do_produce 结尾加 split 提取 ──
OLD_D = '''        # 人物设计环节：拆成 N 个文件（每人一份）
        _pkey2 = phase_cfg.get("key") or phase_cfg.get("name") or ""
        if "人物设计" in _pkey2 and out.exists() and out.stat().st_size > 0:
            try:
                _split_renwu(out, app["key"])
            except Exception as _e:
                print(f"   [拆分失败] {_e}")
    return out'''

NEW_D = '''        # 人物设计环节：拆成 N 个文件（每人一份）
        _pkey2 = phase_cfg.get("key") or phase_cfg.get("name") or ""
        if "人物设计" in _pkey2 and out.exists() and out.stat().st_size > 0:
            try:
                _split_renwu(out, app["key"])
            except Exception as _e:
                print(f"   [拆分失败] {_e}")
        # 通用拆分生产者：从产出里提取 split.json
        if out.exists() and out.stat().st_size > 0:
            try:
                _maybe_extract_split(phase_cfg, out, out_dir)
            except Exception as _e:
                print(f"   [split 提取失败] {_e}")
    return out'''

if OLD_D in text:
    text = text.replace(OLD_D, NEW_D, 1)
    print("[OK] D：do_produce 结尾加 split 提取")
    changed += 1
else:
    print("[FAIL] D")

# ── 补丁 E：在 __main__ 前插入 4 个辅助函数 ──
FUNC_BLOCK = r'''


def _extract_json_block(text):
    """从 AI 输出里提取 json 代码块，返回解析后的 dict 或 None。"""
    import re as _re, json as _json
    if not text:
        return None
    m = _re.search(r"```json\s*\n(.*?)\n```", text, flags=_re.DOTALL | _re.IGNORECASE)
    if not m:
        return None
    try:
        return _json.loads(m.group(1))
    except Exception:
        return None


def _get_split_spec(phase_cfg, out_dir):
    """按环节名读上游 split.json，返回 spec dict 或 None。"""
    import json as _json
    name = phase_cfg.get("name") or phase_cfg.get("key") or ""
    src_name = SPLIT_SOURCES.get(name)
    if not src_name:
        return None
    src_dir = Path(out_dir).parent / src_name
    split_json = src_dir / "split.json"
    if not split_json.exists():
        print(f"   [split] 上游 split.json 不存在：{split_json}")
        return None
    try:
        return _json.loads(split_json.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"   [split] 读 split.json 失败：{e}")
        return None


def _maybe_extract_split(phase_cfg, main_path, out_dir):
    """如果本环节是 split 生产者，从产出提取 JSON 并写 split.json。"""
    import json as _json
    name = phase_cfg.get("name") or phase_cfg.get("key") or ""
    if name not in SPLIT_PRODUCERS:
        return
    try:
        text = Path(main_path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"   [split] 读产出失败：{e}")
        return
    data = _extract_json_block(text)
    if not data:
        print(f"   [split] 未找到 JSON 块：{Path(main_path).name}")
        return
    data["环节"] = phase_cfg.get("code") or ""
    data["环节名"] = name
    out_json = Path(out_dir) / "split.json"
    out_json.write_text(_json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   [split] 已写出：{out_json.name}（{len(data.get('列表') or [])} 项）")


def _do_produce_split(agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
                       input_text, out_dir, dry, extra_note, ai_assist, split_spec):
    """通用拆分引擎：按 split_spec['列表'] 循环调 AI，每项独立落盘。"""
    import json as _json
    items = split_spec.get("列表") or []
    if not items:
        return []

    _versions_dir = Path(out_dir) / "versions"
    _versions_dir.mkdir(parents=True, exist_ok=True)

    _tpl = compose_prompt("PROMPT_PRODUCE.md", program)
    _base_note = format_note(program, phase_cfg) or ""
    if extra_note:
        _base_note = (_base_note + "\n\n【上一轮终审反对意见（必须逐条对应处理）】\n" + extra_note).strip()

    _phase_name = phase_cfg.get("key") or phase_cfg.get("name") or ""
    _produced = []

    for _idx, item in enumerate(items, start=1):
        _key = item.get("key") or item.get("任务名") or item.get("name") or f"item{_idx}"
        _safe = _key.replace("/", "_").replace("\\", "_").replace(":", "_").strip()[:40]
        _out = _versions_dir / f"{chunk_id}__{app['key']}__{_safe}.md"

        _item_note = (_base_note + "\n\n【本次任务（只做这一项，不要处理其他项）】\n"
                       + _json.dumps(item, ensure_ascii=False, indent=2))
        _label = f"{program} › {_phase_name} › {_key}"

        if ai_assist:
            _task = tasks_mod.build_scaffold_task(app, _tpl, input_text, str(_out), _label)
        else:
            _task = tasks_mod.build_produce_task(
                app, _tpl, input_text, str(_out),
                _label, f"{chunk_label} · {_key}", _item_note
            )

        _ok = run_task(agent, _task, dry,
                        title=f"产出 | {app['label']} | {_phase_name} | {_key}",
                        app=app)

        if _ok and not dry:
            wait_file(_out, timeout=60)
            if not (_out.exists() and _out.stat().st_size > 0):
                try:
                    import sys as _s
                    _wu = HERE.parent
                    if str(_wu) not in _s.path:
                        _s.path.insert(0, str(_wu))
                    from mix_send import capture_with_meta as _cap
                    _r0 = _cap(app["key"])
                    _baseline = ((_r0 or {}).get("text", "") if isinstance(_r0, dict) else str(_r0 or "")).strip()
                    _txt = ""
                    for _try in range(30):
                        _r = _cap(app["key"])
                        _cur = ((_r or {}).get("text", "") if isinstance(_r, dict) else str(_r or "")).strip()
                        if _cur and len(_cur) >= 50 and _cur != _baseline:
                            _txt = _cur
                            break
                        time.sleep(6)
                    if _txt:
                        _out.write_text(_txt, encoding="utf-8")
                        print(f"   [{_key}] capture 落盘：{_out.name}")
                except Exception as _e:
                    print(f"   [{_key}] capture 失败：{_e}")

        if dry:
            _produced.append(_out)
            print(f"   [{_key}] (dry-run) {_out.name}")
        elif _out.exists() and _out.stat().st_size > 0:
            _produced.append(_out)
            print(f"   [{_key}] [OK] {_out.name}")
        else:
            print(f"   [{_key}] [FAIL] 无产出")

    return _produced
'''

anchor = '\nif __name__ == "__main__":'
i_main = text.find(anchor)
if i_main < 0:
    print("[FAIL] E：找不到 __main__ 锚点")
elif "_do_produce_split" in text:
    print("[SKIP] E：函数已存在")
else:
    before = text[:i_main].rstrip()
    after = text[i_main:]
    text = before + "\n\n\n" + FUNC_BLOCK.strip() + "\n\n" + after.lstrip("\n")
    print("[OK] E：插入 4 个辅助函数（_extract_json_block / _get_split_spec / _maybe_extract_split / _do_produce_split）")
    changed += 1

# ── 写回 ──
if changed >= 5:
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回：{TARGET.name}（共 {changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处，未写回（避免半成品）")
