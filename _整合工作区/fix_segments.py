# fix_segments.py — chunks_for_phase 支持 segment_mode（volume 按卷纲 / chapters 按章段）
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

OLD = '''def chunks_for_phase(cfg, program, phase_cfg) -> list:
    """把一个环节切成若干「块」。返回 [(chunk_id, chunk_label, standard_block), ...]

    规划：环节即块（desc 作为说明）
    写作：分布/正文 按六要素切 6 块；其余环节单块
    润色：按 4 节切
    质检：按 qcSecs 每节一块
    """
    key = phase_cfg["key"]
'''

NEW = '''def _parse_volumes():
    """从 00_初始化/1.6_卷纲.md 解析卷划分，返回 [(卷名, 起章, 止章), ...]。
    匹配形如：## 第一卷：...（第1-30章）"""
    import re
    p = _project_root() / "00_初始化" / "1.6_卷纲.md"
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8", errors="ignore")
    out = []
    for m in re.finditer(r"##\\s*(第[一二三四五六七八九十百]+卷)[：:][^\\n]*?第\\s*(\\d+)\\s*[-—～~]\\s*(\\d+)\\s*章", text):
        out.append((m.group(1), int(m.group(2)), int(m.group(3))))
    return out


def chunks_for_phase(cfg, program, phase_cfg) -> list:
    """把一个环节切成若干「块」。返回 [(chunk_id, chunk_label, standard_block), ...]

    规划：环节即块（desc 作为说明）；P16 volume 按卷纲切，P17 chapters 按 segment_size 切
    写作：分布/正文 按六要素切 6 块；其余环节单块
    润色：按 4 节切
    质检：按 qcSecs 每节一块
    """
    key = phase_cfg["key"]

    # P16：按卷切（从 1.6_卷纲.md 读真实区间）
    if phase_cfg.get("segment_mode") == "volume":
        vols = _parse_volumes()
        if vols:
            return [(v[0], f"{v[0]}（第{v[1]}-{v[2]}章）", "") for v in vols]
        # 兜底：从 cfg 读卷数
        n = cfg.get("卷数") or 3
        total = cfg.get("章节数") or 150
        per = total // n
        out = []
        for i in range(n):
            s = i * per + 1
            e = (i + 1) * per if i < n - 1 else total
            out.append((f"V{i+1}", f"第{i+1}卷（{s}-{e}章）", ""))
        return out

    # P17：按 segment_size 章一段切
    if phase_cfg.get("segment_mode") == "chapters":
        size = phase_cfg.get("segment_size") or 30
        total = cfg.get("章节数") or 150
        out = []
        for s in range(0, total, size):
            e = min(s + size, total)
            out.append((f"{s+1}-{e}", f"{s+1}-{e}章", ""))
        return out
'''

text = TARGET.read_text(encoding="utf-8")

if "_parse_volumes" in text:
    print("已改过")
elif OLD not in text:
    print("找不到 chunks_for_phase 锚点")
else:
    bak = TARGET.with_suffix(".py.bak_segments")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已加 _parse_volumes + segment_mode 分支")