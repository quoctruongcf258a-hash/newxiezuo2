import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''        if not _skip_check:
            _versions_dir_chk = Path(out_dir) / "versions"
            if _versions_dir_chk.exists():
                for _ai_dir in _versions_dir_chk.iterdir():
                    if not _ai_dir.is_dir():
                        continue
                    _ai = _ai_dir.name
                    if _ai not in _expect_ais:
                        continue
                    _out_ais.add(_ai)
                    for _f in _ai_dir.glob("*.md"):
                        if _f.stat().st_size > 0:
                            _out_pairs.add((_ai, _f.stem))
                            _split_mode = True

            _missing_ais = _expect_ais - _out_ais
            if _split_mode:
                _phase_label = phase_cfg.get("key") or phase_cfg.get("name") or "?"
                print(f"  [产出校验] {_phase_label}：共 {len(_out_pairs)} 份产出，覆盖 {len(_out_ais)}/{len(_expect_ais)} 个 AI")
                if _missing_ais:
                    print(f"  [产出校验] ⚠ 未产出 AI：{_missing_ais}")
            else:
                print(f"  [产出校验] 期望 {len(_expect_ais)} 个，落盘 {len(_out_ais)} 个")
                if _missing_ais:
                    print(f"  [产出校验] ⚠ 未落盘：{_missing_ais}")'''

NEW = '''        if not _skip_check:
            # 目录式命名：<versions>/<ai>/<item>.md
            # 优先用 versions 列表（dry-run 时会伪造，保证 dry 也能校验）
            for v in versions:
                if not v:
                    continue
                _parts = v.parts
                # 找 versions 段，取它后面两段
                try:
                    _vi = _parts.index("versions")
                    if len(_parts) > _vi + 2:
                        _ai = _parts[_vi + 1]
                        _item = _parts[_vi + 2].rsplit(".", 1)[0]
                        _out_ais.add(_ai)
                        _out_pairs.add((_ai, _item))
                        _split_mode = True
                except (ValueError, IndexError):
                    # 兼容旧式 2 段/3 段命名
                    _stem_parts = v.stem.split("__")
                    if len(_stem_parts) >= 3:
                        _split_mode = True
                        _out_ais.add(_stem_parts[1])
                        _out_pairs.add((_stem_parts[1], "__".join(_stem_parts[2:])))
                    elif len(_stem_parts) == 2:
                        _out_ais.add(_stem_parts[-1])

            _missing_ais = _expect_ais - _out_ais
            if _split_mode:
                _phase_label = phase_cfg.get("key") or phase_cfg.get("name") or "?"
                print(f"  [产出校验] {_phase_label}：共 {len(_out_pairs)} 份产出，覆盖 {len(_out_ais)}/{len(_expect_ais)} 个 AI")
                if _missing_ais:
                    print(f"  [产出校验] ⚠ 未产出 AI：{_missing_ais}")
            else:
                print(f"  [产出校验] 期望 {len(_expect_ais)} 个，落盘 {len(_out_ais)} 个")
                if _missing_ais:
                    print(f"  [产出校验] ⚠ 未落盘：{_missing_ais}")'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_check_v3")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已修复：产出校验从 versions 列表拿信息")
else:
    print("[FAIL] 找不到锚点")
    i = text.find("_versions_dir_chk")
    if i >= 0:
        print("\n附近代码：")
        print(text[max(0,i-100):i+800])
