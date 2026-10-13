import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 在 run_mesh_phase 的 chunks 之后加"批量模式短路"
OLD = '''    out_dir = phase_dir(program, chapter, phase_cfg["key"])
    chunks = custom_chunks or chunks_for_phase(cfg, program, phase_cfg)

    print(f"\\n{'=' * 74}")'''

NEW = '''    out_dir = phase_dir(program, chapter, phase_cfg["key"])
    chunks = custom_chunks or chunks_for_phase(cfg, program, phase_cfg)

    #  批量模式短路：如果本环节走拆分引擎，整个环节按 产出盲审拼接 一体化跑 
    _batch_split_spec = None
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
        )

    print(f"\\n{'=' * 74}")'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_batch_hook2")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已把批量模式挂进 run_mesh_phase")
else:
    print("[FAIL] 找不到锚点")
    i = text.find('chunks = custom_chunks or chunks_for_phase')
    if i >= 0:
        print("\n附近代码：")
        print(text[max(0,i-100):i+500])
