import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

changed = 0

# ── 修复 1：去掉 do_produce 里重复的 _chunk_overlaps_stage 调用 ──
OLD1 = '''    # ── 通用拆分：按上游 split.json 循环调 AI ──
    _split_spec = _get_split_spec(phase_cfg, out_dir, chunk_id)
    if _split_spec is not None:
        # 先检查当前 chunk 是否与当前阶段有交集，无交集则整块跳过
        if not _chunk_overlaps_stage(chunk_id, out_dir):
            print(f"   [split] chunk {chunk_id} 与当前阶段无交集，整块跳过")
            return []
        if _split_spec.get("列表"):
            return _do_produce_split(
                agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
                input_text, out_dir, dry, extra_note=extra_note,
                ai_assist=ai_assist, split_spec=_split_spec
            )
        else:
            print(f"   [split] 过滤后列表为空，跳过（{chunk_id}）")
            return []'''

NEW1 = '''    # ── 通用拆分：按上游 split.json 循环调 AI ──
    _split_spec = _get_split_spec(phase_cfg, out_dir, chunk_id)
    if _split_spec is not None:
        if _split_spec.get("列表"):
            return _do_produce_split(
                agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
                input_text, out_dir, dry, extra_note=extra_note,
                ai_assist=ai_assist, split_spec=_split_spec
            )
        else:
            # _get_split_spec 内部已完成 chunk 过滤并打印原因，这里静默跳过
            return []'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 修复1：去掉 do_produce 里重复的 chunk 检查")
    changed += 1
else:
    print("[FAIL] 修复1 找不到锚点")

# ── 修复 2：汇总产出校验在 versions 为空时直接跳过 ──
OLD2 = '''        # 汇总产出校验（兼容 2 段式和 3 段式命名）
        # 2 段式：<chunk>__<AI>.md
        # 3 段式：<chunk>__<AI>__<item>.md
        _expect_ais = {w["key"] for w in writers}
        _out_ais = set()
        _out_pairs = set()      # (AI, item)
        _split_mode = False'''

NEW2 = '''        # 汇总产出校验（兼容 2 段式和 3 段式命名）
        # 2 段式：<chunk>__<AI>.md
        # 3 段式：<chunk>__<AI>__<item>.md
        # 若 versions 为空（chunk 被阶段过滤跳过），直接跳过校验，不报错
        if not versions:
            print(f"  [产出校验] 本 chunk 无产出（可能被阶段过滤跳过）")
            _skip_check = True
        else:
            _skip_check = False
        _expect_ais = {w["key"] for w in writers}
        _out_ais = set()
        _out_pairs = set()      # (AI, item)
        _split_mode = False'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 修复2：产出校验加空产出跳过")
    changed += 1
else:
    print("[FAIL] 修复2 找不到锚点")

# 把校验主体包在 if not _skip_check 里
OLD3 = '''        for v in versions:
            if not v:
                continue
            _parts = v.stem.split("__")
            if len(_parts) >= 3:
                _split_mode = True
                _ai = _parts[1]
                _item = "__".join(_parts[2:])
                _out_ais.add(_ai)
                _out_pairs.add((_ai, _item))
            elif len(_parts) == 2:
                _out_ais.add(_parts[-1])

        _missing_ais = _expect_ais - _out_ais
        if _split_mode:
            _phase_label = phase_cfg.get("key") or phase_cfg.get("name") or "?"
            print(f"  [产出校验] {_phase_label}：共 {len(_out_pairs)} 份拆分产出，覆盖 {len(_out_ais)}/{len(_expect_ais)} 个 AI")
            if _missing_ais:
                print(f"  [产出校验] ⚠ 未产出 AI：{_missing_ais}")
        else:
            print(f"  [产出校验] 期望 {len(_expect_ais)} 个，落盘 {len(_out_ais)} 个")
            if _missing_ais:
                print(f"  [产出校验] ⚠ 未落盘：{_missing_ais}")'''

NEW3 = '''        if not _skip_check:
            for v in versions:
                if not v:
                    continue
                _parts = v.stem.split("__")
                if len(_parts) >= 3:
                    _split_mode = True
                    _ai = _parts[1]
                    _item = "__".join(_parts[2:])
                    _out_ais.add(_ai)
                    _out_pairs.add((_ai, _item))
                elif len(_parts) == 2:
                    _out_ais.add(_parts[-1])

            _missing_ais = _expect_ais - _out_ais
            if _split_mode:
                _phase_label = phase_cfg.get("key") or phase_cfg.get("name") or "?"
                print(f"  [产出校验] {_phase_label}：共 {len(_out_pairs)} 份拆分产出，覆盖 {len(_out_ais)}/{len(_expect_ais)} 个 AI")
                if _missing_ais:
                    print(f"  [产出校验] ⚠ 未产出 AI：{_missing_ais}")
            else:
                print(f"  [产出校验] 期望 {len(_expect_ais)} 个，落盘 {len(_out_ais)} 个")
                if _missing_ais:
                    print(f"  [产出校验] ⚠ 未落盘：{_missing_ais}")'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 修复3：校验主体包在 if not _skip_check 里")
    changed += 1
else:
    print("[FAIL] 修复3 找不到锚点")

# 写回
if changed >= 2:
    bak = TARGET.with_suffix(".py.bak_check_skip")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回（{changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处")
