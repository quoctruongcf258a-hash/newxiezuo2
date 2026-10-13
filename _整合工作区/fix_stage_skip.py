import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 修复 1：_get_split_spec 里 filtered 为空时返回 {"列表": []}
OLD1 = '''    if mode == "current_stage_merged":
        merged_key = f"阶段{stage.get('阶段号')}_{s_start}-{s_end}"
        data["列表"] = [{
            "key": merged_key,
            "name": f"阶段{stage.get('阶段号')}（{s_start}-{s_end}章）",
            "起章": s_start,
            "止章": s_end,
            "子项": filtered,
        }]
        print(f"   [split] 阶段{stage.get('阶段号')}（{s_start}-{s_end}章）：合并为 1 个任务，含 {len(filtered)} 子项")
    elif mode == "current_stage_split":
        data["列表"] = filtered
        print(f"   [split] 阶段{stage.get('阶段号')}（{s_start}-{s_end}章）：过滤后 {len(filtered)} 个任务")'''

NEW1 = '''    if mode == "current_stage_merged":
        if not filtered:
            print(f"   [split] 阶段{stage.get('阶段号')} 与当前 chunk 无交集，跳过")
            data["列表"] = []
            return data
        merged_key = f"阶段{stage.get('阶段号')}_{s_start}-{s_end}"
        data["列表"] = [{
            "key": merged_key,
            "name": f"阶段{stage.get('阶段号')}（{s_start}-{s_end}章）",
            "起章": s_start,
            "止章": s_end,
            "子项": filtered,
        }]
        print(f"   [split] 阶段{stage.get('阶段号')}（{s_start}-{s_end}章）：合并为 1 个任务，含 {len(filtered)} 子项")
    elif mode == "current_stage_split":
        if not filtered:
            print(f"   [split] 阶段{stage.get('阶段号')} 与当前 chunk 无交集，跳过")
            data["列表"] = []
            return data
        data["列表"] = filtered
        print(f"   [split] 阶段{stage.get('阶段号')}（{s_start}-{s_end}章）：过滤后 {len(filtered)} 个任务")'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 修复1：_get_split_spec 过滤为空时返回空列表")
else:
    print("[FAIL] 修复1 找不到锚点")

# 修复 2：do_produce 里返回空列表时直接跳过
OLD2 = '''    # ── 通用拆分：按上游 split.json 循环调 AI ──
    _split_spec = _get_split_spec(phase_cfg, out_dir)
    if _split_spec and _split_spec.get("列表"):
        return _do_produce_split(
            agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
            input_text, out_dir, dry, extra_note=extra_note,
            ai_assist=ai_assist, split_spec=_split_spec
        )'''

NEW2 = '''    # ── 通用拆分：按上游 split.json 循环调 AI ──
    _split_spec = _get_split_spec(phase_cfg, out_dir)
    if _split_spec is not None:
        if _split_spec.get("列表"):
            return _do_produce_split(
                agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
                input_text, out_dir, dry, extra_note=extra_note,
                ai_assist=ai_assist, split_spec=_split_spec
            )
        else:
            # split 模式已启用，但当前 chunk 与阶段无交集 → 跳过（不产出）
            return []'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 修复2：do_produce 空列表时跳过")
else:
    print("[FAIL] 修复2 找不到锚点")

# 写回
bak = TARGET.with_suffix(".py.bak_stage_skip")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")
TARGET.write_text(text, encoding="utf-8")
print(f"[OK] 已写回：{TARGET.name}")
