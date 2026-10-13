import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 找到 do_produce 里的拆分分支
OLD = '''    # ── 通用拆分：按上游 split.json 循环调 AI ──
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

NEW = '''    # ── 通用拆分：按上游 split.json 批量产出（1 条命令生成 N 文件）──
    _split_spec = _get_split_spec(phase_cfg, out_dir, chunk_id)
    if _split_spec is not None:
        if _split_spec.get("列表"):
            # 批量模式：1 条命令，让 AI 自己生成全部文件
            return _do_produce_batch(
                agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
                input_text, out_dir, dry, extra_note=extra_note,
                ai_assist=ai_assist, split_spec=_split_spec,
            )
        else:
            return []'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_batch_hook")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已把批量模式挂进 do_produce")
else:
    print("[FAIL] 找不到 do_produce 里的拆分分支锚点")
    i = text.find("_get_split_spec(phase_cfg, out_dir, chunk_id)")
    if i >= 0:
        print("\n附近代码：")
        print(text[max(0,i-200):i+600])
