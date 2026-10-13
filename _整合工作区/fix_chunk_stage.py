import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 1. 加两个辅助函数
FUNC = '''


def _chunk_range(chunk_id):
    """从 chunk_id 解析起止章，如 '1-30' -> (1, 30)；解析不出返回 None。"""
    import re as _re
    m = _re.match(r"^(\\d+)-(\\d+)$", str(chunk_id).strip())
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def _chunk_overlaps_stage(chunk_id, out_dir):
    """检查 chunk 是否与当前阶段有交集。无法解析或无阶段时返回 True（不跳过）。"""
    r = _chunk_range(chunk_id)
    if not r:
        return True
    stage = _get_current_stage(out_dir)
    if not stage:
        return True
    s_start = stage.get("起章") or 1
    s_end = stage.get("止章") or 99999
    c_start, c_end = r
    return c_end >= s_start and c_start <= s_end
'''

anchor = "def _get_split_spec(phase_cfg, out_dir):"
if "_chunk_overlaps_stage" not in text:
    text = text.replace(anchor, FUNC.strip() + "\n\n\n" + anchor, 1)
    print("[OK] 加 _chunk_range / _chunk_overlaps_stage")

# 2. do_produce 的 split 分支加 chunk 检查
OLD = '''    # ── 通用拆分：按上游 split.json 循环调 AI ──
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

NEW = '''    # ── 通用拆分：按上游 split.json 循环调 AI ──
    _split_spec = _get_split_spec(phase_cfg, out_dir)
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

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] do_produce 加 chunk 阶段检查")
else:
    print("[FAIL] 找不到 do_produce split 分支锚点")

# 3. _get_split_spec 的 filtered 也要用 chunk 过滤
OLD2 = '''    s_start = stage.get("起章") or 1
    s_end = stage.get("止章") or 99999
    items = data.get("列表") or []
    filtered = []
    for it in items:
        it_start = it.get("start") or it.get("起章") or 0
        it_end = it.get("end") or it.get("止章") or 0
        if it_end and it_start and it_end >= s_start and it_start <= s_end:
            filtered.append(it)
        elif it_end == 0:
            filtered.append(it)'''

NEW2 = '''    s_start = stage.get("起章") or 1
    s_end = stage.get("止章") or 99999
    # chunk 范围（用于二次过滤）
    _cr = _chunk_range(chunk_id) if chunk_id else None
    c_start, c_end = _cr if _cr else (0, 99999)
    items = data.get("列表") or []
    filtered = []
    for it in items:
        it_start = it.get("start") or it.get("起章") or 0
        it_end = it.get("end") or it.get("止章") or 0
        if it_end == 0:
            filtered.append(it)
            continue
        # 同时满足：在阶段范围内 + 在 chunk 范围内
        if it_end >= s_start and it_start <= s_end and it_end >= c_start and it_start <= c_end:
            filtered.append(it)'''

if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    print("[OK] _get_split_spec 加 chunk 二次过滤")
else:
    print("[WARN] _get_split_spec 找不到锚点（可能需要传 chunk_id 参数）")

# 4. _get_split_spec 签名加 chunk_id
OLD3 = 'def _get_split_spec(phase_cfg, out_dir):'
NEW3 = 'def _get_split_spec(phase_cfg, out_dir, chunk_id=None):'
if OLD3 in text and "chunk_id=None" not in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] _get_split_spec 签名加 chunk_id")

# 5. 调用点也传 chunk_id
OLD4 = '_split_spec = _get_split_spec(phase_cfg, out_dir)'
NEW4 = '_split_spec = _get_split_spec(phase_cfg, out_dir, chunk_id)'
text = text.replace(OLD4, NEW4)

# 6. dry-run 伪造 versions 也传 chunk_id
OLD5 = '_split_spec_dry = _get_split_spec(phase_cfg, out_dir)'
NEW5 = '_split_spec_dry = _get_split_spec(phase_cfg, out_dir, cid)'
if OLD5 in text:
    text = text.replace(OLD5, NEW5, 1)

# 写回
bak = TARGET.with_suffix(".py.bak_chunk_stage")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")
TARGET.write_text(text, encoding="utf-8")
print(f"[OK] 已写回：{TARGET.name}")
