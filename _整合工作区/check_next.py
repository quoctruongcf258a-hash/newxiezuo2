# check_next.py — 看 W0 是否有 format_note 分支、segment_mode 是否被读
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()

print("=" * 30, "W0 / 细纲 相关引用", "=" * 30)
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ["W0", "细纲分析", "segment_mode", "segment_size",
                              "volume", "chapters", "分段"]):
        print(f"{i:4d}| {ln}")

print()
print("=" * 30, "format_note 里有没有 写作 分支", "=" * 30)
for i, ln in enumerate(lines, 1):
    if "program ==" in ln or 'if program' in ln:
        print(f"{i:4d}| {ln}")