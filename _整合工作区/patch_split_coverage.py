import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_validate_split_coverage" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_split_coverage")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# ── 1. 插入两个辅助函数（放在 _maybe_extract_split 前） ──
FUNC = r'''


def _validate_split_coverage(data, expected_total=None):
    """校验 split.json 的卷覆盖度。返回 (ok, msg)"""
    if not isinstance(data, dict):
        return False, "不是 dict"
    items = data.get("列表") or []
    if not items:
        return False, "列表为空"

    parsed = []
    for i, it in enumerate(items):
        s = it.get("start")
        e = it.get("end")
        if s is None or e is None:
            return False, f"第 {i+1} 项缺 start/end"
        try:
            s, e = int(s), int(e)
        except Exception:
            return False, f"第 {i+1} 项 start/end 不是整数"
        if s >= e:
            return False, f"第 {i+1} 项 start({s}) >= end({e})"
        parsed.append((s, e, it.get("key") or f"卷{i+1}"))

    parsed.sort(key=lambda x: x[0])

    if parsed[0][0] != 1:
        return False, f"卷1 start={parsed[0][0]}，应该从 1 开始"

    for i in range(1, len(parsed)):
        prev_end = parsed[i-1][1]
        cur_start = parsed[i][0]
        if cur_start != prev_end + 1:
            if cur_start <= prev_end:
                return False, f"卷「{parsed[i][2]}」start={cur_start} 与上一卷 end={prev_end} 重叠"
            else:
                return False, f"卷「{parsed[i][2]}」start={cur_start} 与上一卷 end={prev_end} 之间有断档"

    if expected_total is not None:
        last_end = parsed[-1][1]
        if last_end != expected_total:
            return False, f"最后一卷 end={last_end}，应等于总章数 {expected_total}"

    return True, f"✅ 覆盖完整：{len(parsed)} 卷，1-{parsed[-1][1]}"


def _get_expected_total_chapters():
    """从项目信息.json 读章节数。"""
    import json as _json
    try:
        proj_root = _project_root()
        info = proj_root / "00_初始化" / "项目信息.json"
        if info.exists():
            data = _json.loads(info.read_text(encoding="utf-8"))
            return int(data.get("章节数") or 0)
    except Exception:
        pass
    return None
'''

anchor = "def _maybe_extract_split(phase_cfg, main_path, out_dir):"
if anchor in text:
    text = text.replace(anchor, FUNC.strip() + "\n\n\n" + anchor, 1)
    print("[OK] 插入两个辅助函数")
else:
    print("[FAIL] 找不到 _maybe_extract_split 锚点")
    raise SystemExit(1)

# ── 2. 改 _maybe_extract_split 的写入段 ──
OLD = '''    data = _extract_json_block(text)
    if not data:
        print(f"   [split] 未找到 JSON 块：{Path(main_path).name}")
        return
    data["环节"] = phase_cfg.get("code") or ""
    data["环节名"] = name
    out_json = Path(out_dir) / "split.json"
    out_json.write_text(_json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   [split] 已写出：{out_json.name}（{len(data.get('列表') or [])} 项）")'''

NEW = '''    data = _extract_json_block(text)
    if not data:
        print(f"   [split] 未找到 JSON 块：{Path(main_path).name}")
        return

    # ── 覆盖度校验 ──
    _expected = _get_expected_total_chapters()
    _ok, _msg = _validate_split_coverage(data, expected_total=_expected)
    if not _ok:
        print(f"   [split] ❌ 校验失败（{Path(main_path).name}）：{_msg}")
        print(f"   [split]    不写入 split.json，等待其他 AI 的合规版本")
        return

    data["环节"] = phase_cfg.get("code") or ""
    data["环节名"] = name
    out_json = Path(out_dir) / "split.json"

    # 已有更完整的就不覆盖
    if out_json.exists():
        try:
            _old = _json.loads(out_json.read_text(encoding="utf-8"))
            _old_n = len(_old.get("列表") or [])
            _new_n = len(data.get("列表") or [])
            if _old_n >= _new_n:
                print(f"   [split] 已有更完整的 split.json（旧 {_old_n} 卷 >= 新 {_new_n} 卷），保留旧版")
                return
        except Exception:
            pass

    out_json.write_text(_json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   [split] ✅ 已写出：{out_json.name}（{len(data.get('列表') or [])} 项）{_msg}")'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] 改 _maybe_extract_split 的写入段")
else:
    print("[FAIL] 找不到写入段锚点")

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 已写回")
