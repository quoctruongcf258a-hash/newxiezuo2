import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 找到现有的校验代码块
OLD = '''        # 汇总产出校验
        # 对人物设计环节：版本文件命名是 <人名>__<AI>.md，需要分别统计 AI 和人物
        _pkey_chk = phase_cfg.get("key") or phase_cfg.get("name") or ""
        if "人物设计" in _pkey_chk:
            _out_pairs = set()
            for v in versions:
                if not v:
                    continue
                _parts = v.stem.split("__")
                if len(_parts) >= 2:
                    _out_pairs.add((_parts[0], _parts[-1]))     # (人物, AI)
            _expect_ais = {w["key"] for w in writers}
            _out_ais = {p[1] for p in _out_pairs}
            _missing_ais = _expect_ais - _out_ais
            print(f"  [产出校验] 人物设计：共 {len(_out_pairs)} 份档案，覆盖 {len(_out_ais)} 个 AI")
            if _missing_ais:
                print(f"  [产出校验] ⚠ 未产出 AI：{_missing_ais}")
        else:
            _out_keys = {v.stem.split("__")[-1] for v in versions if v}
            _expect_keys = {w["key"] for w in writers}
            _missing = _expect_keys - _out_keys
            print(f"  [产出校验] 期望 {len(_expect_keys)} 个，落盘 {len(_out_keys)} 个")
            if _missing:
                print(f"  [产出校验] ⚠ 未落盘：{_missing}")'''

NEW = '''        # 汇总产出校验（兼容两种命名：<chunk>__<AI>.md 和 <chunk>__<AI>__<item>.md）
        _expect_ais = {w["key"] for w in writers}
        _out_ais = set()
        _out_pairs = set()   # (AI, item)
        _split_mode = False

        for v in versions:
            if not v:
                continue
            _parts = v.stem.split("__")
            if len(_parts) >= 3:
                # 三段式：chunk__AI__item
                _split_mode = True
                _ai = _parts[1]
                _item = "__".join(_parts[2:])   # item 名可能自己含 __
                _out_ais.add(_ai)
                _out_pairs.add((_ai, _item))
            elif len(_parts) == 2:
                # 两段式：chunk__AI
                _out_ais.add(_parts[-1])

        _missing_ais = _expect_ais - _out_ais

        if _split_mode:
            _phase_label = phase_cfg.get("key") or phase_cfg.get("name") or "?"
            print(f"  [产出校验] {_phase_label}：共 {len(_out_pairs)} 份拆分产出，覆盖 {len(_out_ais)}/{len(_expect_ais)} 个 AI")
            if _missing_ais:
                print(f"  [产出校验] ⚠ 未产出 AI：{_missing_ais}")
        else:
            _missing = _expect_ais - _out_ais
            print(f"  [产出校验] 期望 {len(_expect_ais)} 个，落盘 {len(_out_ais)} 个")
            if _missing:
                print(f"  [产出校验] ⚠ 未落盘：{_missing}")'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_split_chk")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已修复：产出校验统计逻辑（兼容两段/三段式）")
else:
    print("[FAIL] 找不到锚点，打印附近代码：")
    i = text.find("汇总产出校验")
    if i >= 0:
        print(text[i-50:i+800])
    else:
        print("  连'汇总产出校验'都找不到")
