import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_producer_shortcut")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# 精确匹配现有的短路代码
OLD = '''    _batch_split_spec = None
    for _cid_b, _, _ in chunks:
        _sp = _get_split_spec(phase_cfg, out_dir, _cid_b)
        if _sp and _sp.get("列表"):
            _batch_split_spec = _sp
            break
    if _batch_split_spec is not None:'''

NEW = '''    _batch_split_spec = None
    # ① 消费者：读上游 split.json
    for _cid_b, _, _ in chunks:
        _sp = _get_split_spec(phase_cfg, out_dir, _cid_b)
        if _sp and _sp.get("列表"):
            _batch_split_spec = _sp
            break
    # ② 生产者：没有上游 split.json，构造"单件"spec
    if _batch_split_spec is None:
        _phase_name_now = phase_cfg.get("name") or phase_cfg.get("key") or ""
        if _phase_name_now in SPLIT_PRODUCERS:
            _batch_split_spec = {
                "拆分维度": "单件",
                "列表": [{
                    "key": _phase_name_now,
                    "name": _phase_name_now,
                    "start": 0,
                    "end": 0,
                    "note": "整个环节一份产出",
                }],
            }
            print(f"   [短路] 生产者环节「{_phase_name_now}」走批量单件模式")
    if _batch_split_spec is not None:'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 短路补丁已生效")
else:
    print("[FAIL] 找不到锚点")
