import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 用现在实际存在的原始锚点
OLD = '''        # 汇总产出校验
        _out_keys = {v.stem.split("__")[-1] for v in versions if v}
        _expect_keys = {w["key"] for w in writers}
        _missing = _expect_keys - _out_keys
        print(f"  [产出校验] 期望 {len(_expect_keys)} 个，落盘 {len(_out_keys)} 个")
        if _missing:
            print(f"  [产出校验] ⚠ 未落盘：{_missing}")
        if dry and not versions:
            versions = [Path(out_dir) / "versions" / f"{cid}__{w['key']}.md" for w in writers]'''

NEW = '''        # 汇总产出校验（兼容 2 段式和 3 段式命名）
        # 2 段式：<chunk>__<AI>.md
        # 3 段式：<chunk>__<AI>__<item>.md
        _expect_ais = {w["key"] for w in writers}
        _out_ais = set()
        _out_pairs = set()      # (AI, item)
        _split_mode = False

        for v in versions:
            if not v:
                continue
            _parts = v.stem.split("__")
            if len(_parts) >= 3:
                _split_mode = True
                _ai = _parts[1]
                _item = "__".join(_parts[2:])
                _out_ais.add(_ai)
                _out_pairs.add((_ai, _item))
            elif len(_parts) == 2:
                _out_ais.add(_parts[-1])

        _missing_ais = _expect_ais - _out_ais
        if _split_mode:
            _phase_label = phase_cfg.get("key") or phase_cfg.get("name") or "?"
            print(f"  [产出校验] {_phase_label}：共 {len(_out_pairs)} 份拆分产出，覆盖 {len(_out_ais)}/{len(_expect_ais)} 个 AI")
            if _missing_ais:
                print(f"  [产出校验] ⚠ 未产出 AI：{_missing_ais}")
        else:
            print(f"  [产出校验] 期望 {len(_expect_ais)} 个，落盘 {len(_out_ais)} 个")
            if _missing_ais:
                print(f"  [产出校验] ⚠ 未落盘：{_missing_ais}")

        # dry-run 模式且没有产出时，伪造 versions 让下游能继续
        if dry and not versions:
            _pkey_dry = phase_cfg.get("key") or phase_cfg.get("name") or ""
            _split_spec_dry = _get_split_spec(phase_cfg, out_dir)
            if _split_spec_dry and _split_spec_dry.get("列表"):
                _vers_dir = Path(out_dir) / "versions"
                versions = []
                for _it in _split_spec_dry.get("列表") or []:
                    _k = _it.get("key") or _it.get("name") or "item"
                    _safe = str(_k).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                    for w in writers:
                        versions.append(_vers_dir / f"{cid}__{w['key']}__{_safe}.md")
            else:
                versions = [Path(out_dir) / "versions" / f"{cid}__{w['key']}.md" for w in writers]'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_check_v2")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已修复产出校验（兼容 2/3 段式）")
else:
    print("[FAIL] 找不到锚点")
