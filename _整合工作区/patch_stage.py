import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

changed = 0

# D1：SPLIT_SOURCES 升级（元组 + 阶段模式）
OLD_D1 = '''SPLIT_SOURCES = {
    "分卷结构": "全书结构",
    "情绪规划": "全书结构",
    "粗纲规划": "分卷结构",
    "简短细纲规划": "粗纲规划",
    "详细细纲规划": "粗纲规划",
    "前30章章纲": "粗纲规划",
}'''
NEW_D1 = '''SPLIT_SOURCES = {
    "分卷结构":         ("全书结构", None),
    "情绪规划":         ("全书结构", None),
    "粗纲规划":         ("分卷结构", None),
    "简短细纲规划":     ("分卷结构", None),
    "细纲":             ("粗纲规划", "current_stage_merged"),
    "前30章落地章纲":   ("粗纲规划", "current_stage_split"),
}'''
if OLD_D1 in text:
    text = text.replace(OLD_D1, NEW_D1, 1)
    print("[OK] D1：SPLIT_SOURCES 升级")
    changed += 1
else:
    print("[FAIL] D1 找不到锚点")

# D2：_get_current_stage 函数
FUNC_STAGE = '''


def _get_current_stage(out_dir):
    """从项目目录/进度.json 读当前阶段信息。返回 dict（含 阶段号/起章/止章）或 None。"""
    import json as _json
    od = Path(out_dir)
    for p in [od] + list(od.parents):
        pj = p / "进度.json"
        if pj.exists():
            try:
                data = _json.loads(pj.read_text(encoding="utf-8"))
            except Exception:
                return None
            stage_no = data.get("当前阶段") or 1
            for s in data.get("阶段列表") or []:
                if s.get("阶段号") == stage_no:
                    return s
            return None
    return None
'''

if "_get_current_stage" not in text:
    anchor = "def _get_split_spec(phase_cfg, out_dir):"
    if anchor in text:
        text = text.replace(anchor, FUNC_STAGE.strip() + "\n\n\n" + anchor, 1)
        print("[OK] D2：_get_current_stage 函数")
        changed += 1
    else:
        print("[FAIL] D2")
else:
    print("[SKIP] D2")

# D3：_get_split_spec 升级
OLD_D3 = '''def _get_split_spec(phase_cfg, out_dir):
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
        return None'''

NEW_D3 = '''def _get_split_spec(phase_cfg, out_dir):
    """按环节名读上游 split.json，支持阶段过滤。"""
    import json as _json
    name = phase_cfg.get("name") or phase_cfg.get("key") or ""
    src = SPLIT_SOURCES.get(name)
    if not src:
        return None

    if isinstance(src, tuple):
        src_name, mode = src
    else:
        src_name, mode = src, None

    src_dir = Path(out_dir).parent / src_name
    split_json = src_dir / "split.json"
    if not split_json.exists():
        print(f"   [split] 上游 split.json 不存在：{split_json}")
        return None
    try:
        data = _json.loads(split_json.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"   [split] 读 split.json 失败：{e}")
        return None

    if not mode:
        return data

    stage = _get_current_stage(out_dir)
    if not stage:
        print(f"   [split] 找不到当前阶段，按全量走")
        return data

    s_start = stage.get("起章") or 1
    s_end = stage.get("止章") or 99999
    items = data.get("列表") or []
    filtered = []
    for it in items:
        it_start = it.get("start") or it.get("起章") or 0
        it_end = it.get("end") or it.get("止章") or 0
        if it_end and it_start and it_end >= s_start and it_start <= s_end:
            filtered.append(it)
        elif it_end == 0:
            filtered.append(it)

    if mode == "current_stage_merged":
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
        print(f"   [split] 阶段{stage.get('阶段号')}（{s_start}-{s_end}章）：过滤后 {len(filtered)} 个任务")
    else:
        print(f"   [split] 未知 mode：{mode}")

    return data'''

if OLD_D3 in text:
    text = text.replace(OLD_D3, NEW_D3, 1)
    print("[OK] D3：_get_split_spec 升级")
    changed += 1
else:
    print("[FAIL] D3")

if changed >= 3:
    bak = TARGET.with_suffix(".py.bak_stage")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回：{TARGET.name}（{changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处，未写回")
