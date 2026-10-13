import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "注入专家抬头" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_expert_role")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# 在 phase_input 里 parts = [] 之后插入专家抬头
OLD = '''def phase_input(cfg, program, phase_cfg, chapter) -> str:
    """为某环节准备输入材料：上游产物 + 平台约束 + 前情。"""
    parts = []'''

NEW = '''def phase_input(cfg, program, phase_cfg, chapter) -> str:
    """为某环节准备输入材料：上游产物 + 平台约束 + 前情。"""
    parts = []

    # 注入专家抬头（方案 A：放在 input_text 最开头）
    _expert_role = phase_cfg.get("expert_role") or "网文创作专家"
    parts.append(f"# 你是{_expert_role}\\n")'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] phase_input 已注入专家抬头")
else:
    print("[FAIL] 找不到 phase_input 锚点")
    i = text.find("def phase_input")
    if i >= 0:
        print(text[i:i+400])
