import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

changed = 0

# ── 改 A：_read_upstream_for_chapter 里所有 glob 改成目录式 ──
# 原来：p18_dir.glob(f"*__章{ch}.md")  →  现在：p18_dir.glob(f"*/章{ch}.md")
replacements = [
    # P18 章纲
    ('for f in sorted(p18_dir.glob(f"*__章{chapter_no}.md")):',
     'for f in sorted(p18_dir.glob(f"*/章{chapter_no}.md")):'),
    # W1~W4 前序环节
    ('for f in sorted(prev_dir.glob(f"*__章{chapter_no}.md")):',
     'for f in sorted(prev_dir.glob(f"*/章{chapter_no}.md")):'),
    # R1 润色的 W3 正文
    ('for f in sorted(w3_dir.glob(f"*__章{chapter_no}.md")):',
     'for f in sorted(w3_dir.glob(f"*/章{chapter_no}.md")):'),
    # Q1~Q9 的 R1 润色
    ('for f in sorted(r1_dir.glob(f"*__章{chapter_no}.md")):',
     'for f in sorted(r1_dir.glob(f"*/章{chapter_no}.md")):'),
]

for old, new in replacements:
    cnt = text.count(old)
    if cnt > 0:
        text = text.replace(old, new)
        print(f"[OK] 替换 {cnt} 处：{old[:60]}...")
        changed += 1
    else:
        print(f"[SKIP] 找不到：{old[:60]}...")

# ── 改 B：run_mesh_phase 里的产出校验改成目录扫描 ──
OLD_B = '''        # 汇总产出校验（兼容 2 段式和 3 段式命名）
        # 2 段式：<chunk>__<AI>.md
        # 3 段式：<chunk>__<AI>__<item>.md
        # 若 versions 为空（chunk 被阶段过滤跳过），直接跳过校验，不报错
        if not versions:
            print(f"  [产出校验] 本 chunk 无产出（可能被阶段过滤跳过）")
            _skip_check = True
        else:
            _skip_check = False
        _expect_ais = {w["key"] for w in writers}
        _out_ais = set()
        _out_pairs = set()      # (AI, item)
        _split_mode = False

        if not _skip_check:
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
                    print(f"  [产出校验] ⚠ 未落盘：{_missing_ais}")'''

NEW_B = '''        # 汇总产出校验（目录式命名：<versions>/<ai>/<item>.md）
        if not versions:
            print(f"  [产出校验] 本 chunk 无产出（可能被阶段过滤跳过）")
            _skip_check = True
        else:
            _skip_check = False
        _expect_ais = {w["key"] for w in writers}
        _out_ais = set()
        _out_pairs = set()      # (AI, item)
        _split_mode = False

        if not _skip_check:
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

if OLD_B in text:
    text = text.replace(OLD_B, NEW_B, 1)
    print("[OK] 改B：run_mesh_phase 产出校验改为目录扫描")
    changed += 1
else:
    print("[FAIL] 改B 找不到锚点（run_mesh_phase 产出校验段）")

# ── 改 C：dry-run 伪造 versions 也改目录式 ──
OLD_C = '''            if _split_spec_dry and _split_spec_dry.get("列表"):
                _vers_dir = Path(out_dir) / "versions"
                versions = []
                for _it in _split_spec_dry.get("列表") or []:
                    _k = _it.get("key") or _it.get("name") or "item"
                    _safe = str(_k).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                    for w in writers:
                        versions.append(_vers_dir / f"{cid}__{w['key']}__{_safe}.md")'''

NEW_C = '''            if _split_spec_dry and _split_spec_dry.get("列表"):
                _vers_dir = Path(out_dir) / "versions"
                versions = []
                for _it in _split_spec_dry.get("列表") or []:
                    _k = _it.get("key") or _it.get("name") or "item"
                    _safe = str(_k).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                    for w in writers:
                        versions.append(_vers_dir / w["key"] / f"{_safe}.md")'''

if OLD_C in text:
    text = text.replace(OLD_C, NEW_C, 1)
    print("[OK] 改C：dry-run 伪造路径改目录式")
    changed += 1
else:
    print("[FAIL] 改C 找不到锚点（dry-run 伪造段）")

# 写回
if changed >= 2:
    bak = TARGET.with_suffix(".py.bak_workdir2")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回（{changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处，未写回")
