# fix_volumes_fallback.py — _parse_volumes 支持多路径 fallback
import shutil
from pathlib import Path

ORCH = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = ORCH.read_text(encoding="utf-8")

OLD = '''def _parse_volumes():
    """从 00_初始化/1.6_卷纲.md 解析卷划分，返回 [(卷名, 起章, 止章), ...]。
    匹配形如：## 第一卷：...（第1-30章）"""
    import re
    p = _project_root() / "00_初始化" / "1.6_卷纲.md"
    if not p.exists():
        return []
'''

NEW = '''def _parse_volumes():
    """解析卷划分，返回 [(卷名, 起章, 止章), ...]。

    查找顺序（fallback）：
      1. 00_初始化/1.6_卷纲.md         ← 现在
      2. 01_规划/分卷结构/phase_candidate.md  ← 将来（1.6 移到规划后）
      3. 01_规划/分卷结构/merged/分卷结构.md
      4. 01_规划/全书结构/phase_candidate.md
    """
    import re
    root = _project_root()
    candidates = [
        root / "00_初始化" / "1.6_卷纲.md",
        root / "01_规划" / "分卷结构" / "phase_candidate.md",
        root / "01_规划" / "分卷结构" / "merged" / "分卷结构.md",
        root / "01_规划" / "全书结构" / "phase_candidate.md",
    ]
    p = None
    for c in candidates:
        if c.exists() and c.stat().st_size > 0:
            p = c
            break
    if p is None:
        return []
'''

if "将来（1.6 移到规划后）" in text:
    print("已改过")
elif OLD not in text:
    print("✗ 找不到 _parse_volumes 锚点")
    i = text.find("def _parse_volumes")
    if i >= 0:
        print(repr(text[i:i+500]))
else:
    bak = ORCH.with_suffix(".py.bak_volfallback")
    if not bak.exists():
        shutil.copy(ORCH, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    ORCH.write_text(text, encoding="utf-8")
    print("✔ _parse_volumes 已加多路径 fallback")