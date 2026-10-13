import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")
changed = 0

# ── 补丁 1：第 251 行 key 加载加兜底 ─────────────
OLD1 = '''    key = phase_cfg.get("key", "")
    if program == "规划":'''
NEW1 = '''    key = phase_cfg.get("key") or phase_cfg.get("name") or ""
    if program == "规划":'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 补丁1：key 加载加 name 兜底")
    changed += 1
else:
    print("[FAIL] 补丁1 找不到锚点")

# ── 补丁 2：写作阶段 4 个 == 改 in ──────────────
pairs = [
    ('if key == "章前对齐卡":', 'if "章前对齐卡" in key:'),
    ('if key == "分布":',       'if "分布" in key:'),
    ('if key == "正文":',       'if "正文" in key:'),
    ('if key == "章内节奏自检":', 'if "章内节奏自检" in key:'),
]

for old, new in pairs:
    if old in text:
        text = text.replace(old, new, 1)
        print(f"[OK] 补丁2：{old} -> {new}")
        changed += 1
    else:
        print(f"[WARN] 补丁2 找不到：{old}")

# ── 写回（带备份） ─────────────────────────────
if changed:
    bak = TARGET.with_suffix(".py.bak_fmtnote")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"\n已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"已写回：{TARGET.name}（共 {changed} 处修改）")
else:
    print("\n无修改")
