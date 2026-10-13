import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_force_serial" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_force_serial")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

changed = 0

# ── 1. do_produce 签名加 _force_serial ──
OLD1 = '''def do_produce(agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
               input_text, out_dir, dry, extra_note="", ai_assist=False):'''
NEW1 = '''def do_produce(agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
               input_text, out_dir, dry, extra_note="", ai_assist=False,
               _force_serial=None):'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 改1：do_produce 加 _force_serial 参数")
    changed += 1
else:
    print("[FAIL] 改1 找不到 do_produce 签名")

# ── 2. do_produce 里调用 _do_produce_batch 传参 ──
OLD2 = '''            return _do_produce_batch(
                agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
                input_text, out_dir, dry, extra_note=extra_note,
                ai_assist=ai_assist, split_spec=_split_spec,
            )'''
NEW2 = '''            return _do_produce_batch(
                agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
                input_text, out_dir, dry, extra_note=extra_note,
                ai_assist=ai_assist, split_spec=_split_spec,
                _force_serial=_force_serial,
            )'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] 改2：do_produce 传 _force_serial")
    changed += 1
else:
    print("[FAIL] 改2 找不到 _do_produce_batch 调用")

# ── 3. _do_produce_batch 签名加 _force_serial ──
OLD3 = '''def _do_produce_batch(
    agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
    input_text, out_dir, dry, extra_note, ai_assist, split_spec,
):'''
NEW3 = '''def _do_produce_batch(
    agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
    input_text, out_dir, dry, extra_note, ai_assist, split_spec,
    _force_serial=None,
):'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 改3：_do_produce_batch 加 _force_serial 参数")
    changed += 1
else:
    print("[FAIL] 改3 找不到 _do_produce_batch 签名")

# ── 4. _do_produce_batch 读参优先级 ──
OLD4 = '''    # ── 串行/赛马判定 ──
    _is_serial = sess.get("_is_serial_produce", True)
    if _is_serial:'''
NEW4 = '''    # ── 串行/赛马判定 ──
    # 优先用显式传入的 _force_serial，没有才读 sess
    if _force_serial is not None:
        _is_serial = _force_serial
    else:
        _is_serial = sess.get("_is_serial_produce", True)
    print(f"   [判定] _force_serial={_force_serial}，最终 _is_serial={_is_serial}")
    if _is_serial:'''

if OLD4 in text:
    text = text.replace(OLD4, NEW4, 1)
    print("[OK] 改4：_do_produce_batch 优先用 _force_serial")
    changed += 1
else:
    print("[FAIL] 改4 找不到 _is_serial 读取")

# ── 5. _run_batch_mesh 里调用 do_produce 时传 _force_serial ──
OLD5 = '''            def _produce_locked(_w):
                with _get_ai_lock(_w["key"]):
                    return do_produce(agent, sess, _w, program, phase_cfg,
                                       "batch", phase_cfg.get("key") or "",
                                       input_text, out_dir, dry,
                                       ai_assist=False)'''
NEW5 = '''            def _produce_locked(_w):
                with _get_ai_lock(_w["key"]):
                    return do_produce(agent, sess, _w, program, phase_cfg,
                                       "batch", phase_cfg.get("key") or "",
                                       input_text, out_dir, dry,
                                       ai_assist=False,
                                       _force_serial=is_serial_produce)'''

if OLD5 in text:
    text = text.replace(OLD5, NEW5, 1)
    print("[OK] 改5a：_run_batch_mesh 并发分支传 _force_serial")
    changed += 1
else:
    print("[FAIL] 改5a 找不到并发分支")

OLD6 = '''                v = do_produce(agent, sess, w, program, phase_cfg,
                                "batch", phase_cfg.get("key") or "",
                                input_text, out_dir, dry,
                                ai_assist=False)'''
NEW6 = '''                v = do_produce(agent, sess, w, program, phase_cfg,
                                "batch", phase_cfg.get("key") or "",
                                input_text, out_dir, dry,
                                ai_assist=False,
                                _force_serial=is_serial_produce)'''

if OLD6 in text:
    text = text.replace(OLD6, NEW6, 1)
    print("[OK] 改5b：_run_batch_mesh 串行分支传 _force_serial")
    changed += 1
else:
    print("[FAIL] 改5b 找不到串行分支")

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 共修改 {changed} 处")
