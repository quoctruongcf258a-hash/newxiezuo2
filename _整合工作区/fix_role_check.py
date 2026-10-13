# fix_role_check.py — run_mesh_phase 开头加角色覆盖校验
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''    print(f"  [角色] 执行={[p['label'] for p in phase_writers]} "
          f"审核={[p['label'] for p in phase_reviewers]} "
          f"调整={phase_merger['label']}")
'''

NEW = '''    # ─── 角色覆盖校验：确保每个 AI 都有任务 ───
    _all_keys = {p["key"] for p in parts}
    _writer_keys = {p["key"] for p in phase_writers}
    _reviewer_keys = {p["key"] for p in phase_reviewers}

    _missing_w = _all_keys - _writer_keys
    _missing_r = _all_keys - _reviewer_keys

    if _missing_w:
        print(f"  ⚠ [校验] 这些 AI 没被指派为写手：{_missing_w}，自动补入")
        for p in parts:
            if p["key"] in _missing_w:
                phase_writers.append(p)
    if _missing_r:
        print(f"  ⚠ [校验] 这些 AI 没被指派为审核：{_missing_r}，自动补入")
        for p in parts:
            if p["key"] in _missing_r:
                phase_reviewers.append(p)

    print(f"  [角色] 执行={[p['label'] for p in phase_writers]} "
          f"审核={[p['label'] for p in phase_reviewers]} "
          f"调整={phase_merger['label']}")
    print(f"  [校验] 参与者 {len(parts)} 人：写手 {len(phase_writers)} / 审核 {len(phase_reviewers)}")
'''

if "角色覆盖校验" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
    i = text.find("[角色] 执行=")
    if i >= 0:
        print(repr(text[i-200:i+300]))
else:
    bak = TARGET.with_suffix(".py.bak_rolecheck")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已加角色覆盖校验")