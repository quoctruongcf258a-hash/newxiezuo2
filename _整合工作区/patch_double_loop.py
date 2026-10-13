import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_double_loop")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# ── 找 _run_batch_mesh 的【阶段1：产出】段 ──
import re
m = re.search(r"def _run_batch_mesh\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if not m:
    print("[FAIL] 找不到 _run_batch_mesh")
    raise SystemExit(1)

body = m.group(0)
# 找产出段
i1 = body.find("# 阶段1：产出")
if i1 < 0:
    i1 = body.find("阶段1：产出")
i2 = body.find("# 阶段2：盲审", i1) if i1 >= 0 else -1
if i2 < 0:
    i2 = body.find("阶段2：盲审", i1)

if i1 < 0 or i2 < 0:
    print(f"[FAIL] 找不到阶段1边界 i1={i1} i2={i2}")
    raise SystemExit(1)

old_stage1 = body[i1:i2]
print("=" * 70)
print("旧的阶段1（前 500 字）：")
print("=" * 70)
print(old_stage1[:500])

# ── 替换整个阶段1 ──
new_stage1 = '''# 阶段1：产出（把 writers 交给 _do_produce_batch 并发处理，不再双层遍历）
    print(f"\\n{'='*70}\\n【阶段1：产出】{len(writers)} 个 AI 并发\\n{'='*70}")
    all_versions = {}

    # 每个 writer 单独跑一次 _do_produce_batch，但每次排除自己以外的 AI 作为 backup
    # 赛马模式：只跑自己
    # 串行模式：只跑主 AI（其他作为 backup，由 _do_produce_batch 内部处理）
    def _produce_one(_w):
        # 构造一个只含当前 writer 的 sess（避免 _do_produce_batch 遍历全部 AI）
        _sess_sub = dict(sess)
        _sess_sub["participants"] = [_w]
        _sess_sub["_is_serial_produce"] = False   # 单 AI 模式，无兜底
        with _get_ai_lock(_w["key"]):
            return do_produce(agent, _sess_sub, _w, program, phase_cfg,
                               "batch", phase_cfg.get("key") or "",
                               input_text, out_dir, dry,
                               ai_assist=False)

    if not dry and len(writers) > 1:
        with ThreadPoolExecutor(max_workers=len(writers)) as _ex:
            _futs = {_ex.submit(_produce_one, w): w for w in writers}
            for _fut in as_completed(_futs):
                w = _futs[_fut]
                try:
                    v = _fut.result()
                    if isinstance(v, list):
                        all_versions[w["key"]] = v
                        print(f"   ✓ {w['key']} 完成：{len(v)} 个文件")
                    else:
                        print(f"   ✗ {w['key']} 无产出")
                except Exception as _e:
                    print(f"   ✗ {w['key']} 异常：{_e}")
    else:
        for w in writers:
            try:
                v = _produce_one(w)
                if isinstance(v, list):
                    all_versions[w["key"]] = v
                    print(f"   ✓ {w['key']} 完成：{len(v)} 个文件")
            except Exception as _e:
                print(f"   ✗ {w['key']} 异常：{_e}")

    _missing_w = [w["key"] for w in writers if w["key"] not in all_versions]
    if _missing_w:
        print(f"   ⛔ 产出未完成：{_missing_w}")
        return None

    '''

# 用 body 内的替换
new_body = body[:i1] + new_stage1 + body[i2:]
# 替换原文件中的 body
text = text.replace(body, new_body, 1)

TARGET.write_text(text, encoding="utf-8")
print()
print("[OK] 已替换 _run_batch_mesh 的阶段1")
