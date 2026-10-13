# patch_keywords.py — 加 keywords_for_phase 函数 + 在 phase_input 里注入
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")


def main():
    print("=" * 60)
    print("patch_keywords")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "def keywords_for_phase" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_kw")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # ── 1. 在 _upstream_files 之前插入 keywords_for_phase ──
    anchor = "def _upstream_files(program, phase_cfg, chapter=None):\n"
    if anchor not in text:
        print("[失败] 找不到 _upstream_files 锚点")
        return

    func = '''def keywords_for_phase(cfg, program, phase_cfg):
    """从 apps.json 提取本环节关键词，返回 dict。"""
    out = {"内容词": [], "动作词": [], "禁止词": [], "验收词": [], "红线": []}
    key = phase_cfg.get("key") or phase_cfg.get("name") or ""

    if program == "规划":
        for d in cfg.get("auditDirections") or []:
            rings = list(d.get("rings") or []) + list(d.get("extends") or [])
            if key in rings:
                out["验收词"] += list(d.get("standards") or [])
                out["禁止词"] += list(d.get("failPatterns") or [])
                break

    if program == "写作":
        seg = phase_cfg.get("six_segment") or ""
        for e in (cfg.get("sixElements") or {}).get("elements") or []:
            if e.get("key") == seg:
                kws = e.get("keywords") or ""
                out["内容词"] += [x for x in kws.split("・") if x]
                out["验收词"] += list(e.get("standards") or [])
                out["禁止词"] += list(e.get("failPatterns") or [])
        for r in (cfg.get("sixElements") or {}).get("redLines") or []:
            out["红线"].append(f"{r.get('key')}：{r.get('rule')}")
        craft = phase_cfg.get("craft") or ""
        cat = craft.split("(")[0].strip()
        for c in (cfg.get("writingEnvironment") or {}).get("categories") or []:
            if c.get("key") == cat:
                for it in c.get("items") or []:
                    out["动作词"].append(f"{it.get('key')}：{it.get('check')}")
                    if it.get("坑"):
                        out["禁止词"].append(it["坑"])
                break

    if program == "润色":
        for s in (cfg.get("polishStandard") or {}).get("sections") or []:
            for it in s.get("items") or []:
                out["动作词"].append(f"{it.get('name')}：{it.get('check')}")
        out["禁止词"] += list((cfg.get("polishStandard") or {}).get("pitfalls") or [])

    if program == "质检":
        for n in phase_cfg.get("qcSecs") or []:
            for s in (cfg.get("qcStandard") or {}).get("sections") or []:
                if str(s.get("n")) == str(n):
                    out["内容词"] += list(s.get("items") or [])

    return out


def _upstream_files(program, phase_cfg, chapter=None):
'''
    text = text.replace(anchor, func, 1)
    print("✔ 改动1：加了 keywords_for_phase 函数")

    # ── 2. 在 phase_input 里注入关键词块（接在任务说明之后）──
    inject_anchor = '    # _INJECT_DESC：注入本环节的任务说明（来自 rings_items.json 的 desc）\n'
    if inject_anchor not in text:
        print("[失败] 找不到 _INJECT_DESC 锚点")
        return

    # 先找 _INJECT_DESC 那段结尾（到 "    pb = platform_block(cfg)\n"）
    end_anchor = "    pb = platform_block(cfg)\n"
    idx = text.find(inject_anchor)
    end_idx = text.find(end_anchor, idx)
    if end_idx < 0:
        print("[失败] 找不到 _INJECT_DESC 段尾")
        return

    kw_block = '''    # _KEYWORDS：注入本环节关键词（从 apps.json 自动提取）
    try:
        _kw = keywords_for_phase(cfg, program, phase_cfg)
        _kb = "【本环节关键词（落笔时逐条对照）】"
        if _kw["内容词"]:
            _kb += "\\n  内容词：" + "、".join(_kw["内容词"][:10])
        if _kw["动作词"]:
            _kb += "\\n  动作词：" + "、".join(_kw["动作词"][:10])
        if _kw["禁止词"]:
            _kb += "\\n  禁止词：" + "、".join(_kw["禁止词"][:10])
        if _kw["验收词"]:
            _kb += "\\n  验收词：" + "、".join(_kw["验收词"][:10])
        if _kw["红线"]:
            _kb += "\\n  红线：" + "、".join(_kw["红线"])
        if any(_kw.values()):
            parts.append(_kb)
    except Exception:
        pass

'''
    text = text[:end_idx] + kw_block + text[end_idx:]
    print("✔ 改动2：phase_input 里注入关键词块")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()