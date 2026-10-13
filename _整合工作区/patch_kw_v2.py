# patch_kw_v2.py — 关键词块精简（只留内容词/动作词/红线），内容词从 desc 提取
import shutil
import re
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")


def main():
    print("=" * 60)
    print("patch_kw_v2")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_KW_SLIM" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_kw2")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # ── 1. keywords_for_phase：规划程序从 desc 提取内容词 ──
    old_func = '''    if program == "规划":
        for d in cfg.get("auditDirections") or []:
            rings = list(d.get("rings") or []) + list(d.get("extends") or [])
            if key in rings:
                out["验收词"] += list(d.get("standards") or [])
                out["禁止词"] += list(d.get("failPatterns") or [])
                break
'''
    new_func = '''    if program == "规划":
        # _KW_SLIM：内容词从 desc 提取（用 + / → 切分）
        _desc = (phase_cfg.get("desc") or "").strip()
        if _desc:
            for _part in re.split(r"[+→/、，,；;]+", _desc):
                _p = _part.strip()
                if _p and len(_p) <= 12 and not _p.startswith("输出"):
                    out["内容词"].append(_p)
        # 验收/禁止词不再从 auditDirections 加（下面已有完整标准）
'''
    if old_func not in text:
        print("[失败] 找不到 keywords_for_phase 里规划那段")
        return
    text = text.replace(old_func, new_func, 1)
    print("✔ 改动1：规划内容词从 desc 提取")

    # ── 2. 确保顶部 import re ──
    if "\nimport re\n" not in text and "import re\n" not in text[:500]:
        text = text.replace("import argparse\n", "import argparse\nimport re\n", 1)
        print("✔ 改动2：顶部加了 import re")

    # ── 3. 注入块只留 内容词/动作词/红线 ──
    old_block = '''        _kb = "【本环节关键词（落笔时逐条对照）】"
        if _kw["内容词"]:
            _kb += "\\\\n  内容词：" + "、".join(_kw["内容词"][:10])
        if _kw["动作词"]:
            _kb += "\\\\n  动作词：" + "、".join(_kw["动作词"][:10])
        if _kw["禁止词"]:
            _kb += "\\\\n  禁止词：" + "、".join(_kw["禁止词"][:10])
        if _kw["验收词"]:
            _kb += "\\\\n  验收词：" + "、".join(_kw["验收词"][:10])
        if _kw["红线"]:
            _kb += "\\\\n  红线：" + "、".join(_kw["红线"])
        if any(_kw.values()):
            parts.append(_kb)
'''
    new_block = '''        # _KW_SLIM：只留 内容词/动作词/红线（禁止/验收下面已有）
        _kb = "【本环节关键词（落笔时逐条对照）】"
        _has = False
        if _kw["内容词"]:
            _kb += "\\\\n  内容词：" + "、".join(_kw["内容词"][:10])
            _has = True
        if _kw["动作词"]:
            _kb += "\\\\n  动作词：" + "、".join(_kw["动作词"][:10])
            _has = True
        if _kw["红线"]:
            _kb += "\\\\n  红线：" + "、".join(_kw["红线"])
            _has = True
        if _has:
            parts.append(_kb)
'''
    if old_block not in text:
        print("[失败] 找不到关键词注入块（可能转义不同）")
        print("       请把当前 _KEYWORDS 那段发我，我改锚点")
        return
    text = text.replace(old_block, new_block, 1)
    print("✔ 改动3：关键词块只留 内容词/动作词/红线")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()