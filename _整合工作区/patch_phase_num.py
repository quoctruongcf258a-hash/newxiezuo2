import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_fmt_phase_label" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_phase_num")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

changed = 0

# ── 1. 插入 helper 函数（放在 run_mesh_phase 前） ──
FUNC = r'''


def _fmt_phase_label(program, phase_cfg):
    """构造带环节编号的 label：'规划 › 环节2/33 文风与叙事基调'"""
    idx = phase_cfg.get("_idx")
    total = phase_cfg.get("_total")
    key = phase_cfg.get("key") or phase_cfg.get("name") or ""
    if idx and total:
        return f"{program} › 环节{idx}/{total} {key}"
    return f"{program} › {key}"
'''

anchor = "def run_mesh_phase(agent, cfg, sess, program, phase_cfg, chapter, input_text, dry,"
if anchor in text:
    text = text.replace(anchor, FUNC.strip() + "\n\n\n" + anchor, 1)
    print("[OK] 插入 _fmt_phase_label")
else:
    print("[FAIL] 找不到锚点")
    raise SystemExit(1)

# ── 2. run_program 循环里给每个 ph 赋 _idx / _total ──
OLD_LOOP = '''    for ph in phases:'''
NEW_LOOP = '''    _total_phases = len(phases)
    for _idx, ph in enumerate(phases, 1):
        ph["_idx"] = _idx
        ph["_total"] = _total_phases'''

if OLD_LOOP in text:
    text = text.replace(OLD_LOOP, NEW_LOOP, 1)
    print("[OK] run_program 循环加 idx")
    changed += 1
else:
    print("[WARN] 找不到 for ph in phases")

# ── 3. 替换所有 phase_label 构造 ──
patterns = [
    ('    label = f"{program} › {phase_cfg[\'key\']}"',
     '    label = _fmt_phase_label(program, phase_cfg)'),
    ('    _label = f"{program} › {phase_cfg.get(\'key\') or phase_cfg.get(\'name\') or \'\'} › {_name}"',
     '    _label = _fmt_phase_label(program, phase_cfg) + f" › {_name}"'),
    ('        _label = f"{program} › {_phase_name} › {_key}"',
     '        _label = _fmt_phase_label(program, phase_cfg) + f" › {_key}"'),
]

for old, new in patterns:
    cnt = text.count(old)
    if cnt > 0:
        text = text.replace(old, new)
        print(f"[OK] 替换 label 构造：{cnt} 处")
        changed += cnt

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 共修改 {changed} 处")
