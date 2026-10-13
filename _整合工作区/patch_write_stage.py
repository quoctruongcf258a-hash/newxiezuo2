import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

changed = 0

# ── 补丁 1：SPLIT_SOURCES 加 W0~W4 ──
OLD_SRC = '''SPLIT_SOURCES = {
    "分卷结构":         ("全书结构", None),
    "情绪规划":         ("全书结构", None),
    "粗纲规划":         ("分卷结构", None),
    "简短细纲规划":     ("分卷结构", None),
    "细纲":             ("粗纲规划", "current_stage_merged"),
    "前30章落地章纲":   ("粗纲规划", "current_stage_split"),
}'''

NEW_SRC = '''SPLIT_SOURCES = {
    # ── 规划阶段 ──
    "分卷结构":         ("全书结构", None),
    "情绪规划":         ("全书结构", None),
    "粗纲规划":         ("分卷结构", None),
    "简短细纲规划":     ("分卷结构", None),
    "细纲":             ("粗纲规划", "current_stage_merged"),
    "前30章落地章纲":   ("粗纲规划", "current_stage_split"),
    # ── 写作阶段（跨程序读 01_规划/粗纲规划 的章列表，按当前阶段过滤）──
    "W0_细纲分析":      ("01_规划/粗纲规划", "current_stage_split"),
    "W1_章前对齐卡":    ("01_规划/粗纲规划", "current_stage_split"),
    "W2_分布":          ("01_规划/粗纲规划", "current_stage_split"),
    "W3_正文":          ("01_规划/粗纲规划", "current_stage_split"),
    "W4_章内节奏自检":  ("01_规划/粗纲规划", "current_stage_split"),
}'''

if OLD_SRC in text:
    text = text.replace(OLD_SRC, NEW_SRC, 1)
    print("[OK] 补丁1：SPLIT_SOURCES 加 W0~W4")
    changed += 1
else:
    print("[FAIL] 补丁1 找不到锚点")

# ── 补丁 2：_get_split_spec 支持跨程序路径 ──
OLD_GET = '''    src_dir = Path(out_dir).parent / src_name
    split_json = src_dir / "split.json"'''

NEW_GET = '''    # src_name 含 "/" 时按项目根开始（跨程序读），否则按当前 out_dir.parent 找
    if "/" in src_name:
        # 从 out_dir 向上找项目根（含 00_初始化 或 进度.json 的目录）
        _root = Path(out_dir)
        for _p in [_root] + list(_root.parents):
            if (_p / "00_初始化").exists() or (_p / "进度.json").exists():
                _root = _p
                break
        src_dir = _root / src_name
    else:
        src_dir = Path(out_dir).parent / src_name
    split_json = src_dir / "split.json"'''

if OLD_GET in text:
    text = text.replace(OLD_GET, NEW_GET, 1)
    print("[OK] 补丁2：_get_split_spec 支持跨程序路径")
    changed += 1
else:
    print("[FAIL] 补丁2 找不到锚点")

# 写回
if changed >= 2:
    bak = TARGET.with_suffix(".py.bak_write_stage")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回（{changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处，未写回")
