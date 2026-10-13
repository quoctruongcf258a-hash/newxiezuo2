import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 读取 dry-run 伪造块
OLD_DRY = '''        # dry-run 模式且没有产出时，伪造 versions 让下游能继续
        if dry and not versions:
            _pkey_dry = phase_cfg.get("key") or phase_cfg.get("name") or ""
            _split_spec_dry = _get_split_spec(phase_cfg, out_dir, cid)
            if _split_spec_dry and _split_spec_dry.get("列表"):
                _vers_dir = Path(out_dir) / "versions"
                versions = []
                for _it in _split_spec_dry.get("列表") or []:
                    _k = _it.get("key") or _it.get("name") or "item"
                    _safe = str(_k).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                    for w in writers:
                        versions.append(_vers_dir / w["key"] / f"{_safe}.md")
            else:
                versions = [Path(out_dir) / "versions" / f"{cid}__{w['key']}.md" for w in writers]

'''

if OLD_DRY not in text:
    print("[FAIL] 找不到 dry-run 伪造块")
    raise SystemExit(1)

# 删除原位置
text = text.replace(OLD_DRY, "", 1)
print("[OK] 删除原位置的 dry-run 伪造块")

# 插入到校验之前（"# 汇总产出校验" 之前）
ANCHOR = '''        # 汇总产出校验（目录式命名：<versions>/<ai>/<item>.md）'''
NEW_BLOCK = '''        # dry-run 模式且没有产出时，先伪造 versions（让下游校验能跑）
        if dry and not versions:
            _split_spec_dry = _get_split_spec(phase_cfg, out_dir, cid)
            if _split_spec_dry and _split_spec_dry.get("列表"):
                _vers_dir = Path(out_dir) / "versions"
                versions = []
                for _it in _split_spec_dry.get("列表") or []:
                    _k = _it.get("key") or _it.get("name") or "item"
                    _safe = str(_k).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                    for w in writers:
                        versions.append(_vers_dir / w["key"] / f"{_safe}.md")
            else:
                versions = [Path(out_dir) / "versions" / f"{cid}__{w['key']}.md" for w in writers]

        # 汇总产出校验（目录式命名：<versions>/<ai>/<item>.md）'''

if ANCHOR in text:
    text = text.replace(ANCHOR, NEW_BLOCK, 1)
    print("[OK] 插入到校验之前")
else:
    print("[FAIL] 找不到校验锚点")
    raise SystemExit(1)

# 写回
bak = TARGET.with_suffix(".py.bak_order_fix")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")
TARGET.write_text(text, encoding="utf-8")
print("[OK] 已写回")
