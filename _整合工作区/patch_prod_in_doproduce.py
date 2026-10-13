import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_prod_shortcut")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# 找 do_produce 里 _get_split_spec 调用
OLD = '''    _split_spec = _get_split_spec(phase_cfg, out_dir, chunk_id)
    if _split_spec is not None:'''

NEW = '''    _split_spec = _get_split_spec(phase_cfg, out_dir, chunk_id)
    # 生产者环节（SPLIT_PRODUCERS）：构造"单件" spec 走批量
    if _split_spec is None:
        _pname = phase_cfg.get("name") or phase_cfg.get("key") or ""
        if _pname in SPLIT_PRODUCERS:
            _split_spec = {
                "拆分维度": "单件",
                "列表": [{
                    "key": _pname,
                    "name": _pname,
                    "start": 0, "end": 0,
                    "note": "整个环节一份产出",
                }],
            }
    if _split_spec is not None:'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] do_produce 为生产者构造单件 spec")
else:
    print("[FAIL] 找不到锚点")

TARGET.write_text(text, encoding="utf-8")
print(f"[OK] 已写回")
