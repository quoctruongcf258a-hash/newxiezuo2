# find_init.py — 找 00_初始化 的提示词和项目信息.json 生成逻辑
from pathlib import Path

SCRATCH = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

print("=" * 30, "1) _scratch 下所有含 00_ 或 初始化 或 项目信息 的文件", "=" * 30)
for p in SCRATCH.rglob("*"):
    if p.is_file() and any(k in p.name for k in ["初始化", "项目信息", "project_info"]):
        print(f"  {p.relative_to(SCRATCH)}")

print()
print("=" * 30, "2) _scratch 下所有 .md / .json / .py 顶层文件", "=" * 30)
for p in sorted(SCRATCH.iterdir()):
    if p.is_file():
        print(f"  {p.name}  ({p.stat().st_size} 字节)")

print()
print("=" * 30, "3) prompts 目录", "=" * 30)
prompts = SCRATCH / "prompts"
if prompts.exists():
    for p in sorted(prompts.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(prompts)}  ({p.stat().st_size} 字节)")
else:
    print("  没有 prompts 目录")

print()
print("=" * 30, "4) orchestrator.py 里含 初始化 或 项目信息 的行", "=" * 30)
lines = (SCRATCH / "orchestrator.py").read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ["初始化", "项目信息", "PROMPT_INIT", "init_"]):
        print(f"{i:4d}| {ln[:120]}")

print()
print("=" * 30, "5) tasks.py 里含 初始化 或 项目信息 的行", "=" * 30)
tlines = (SCRATCH / "tasks.py").read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(tlines, 1):
    if any(k in ln for k in ["初始化", "项目信息", "PROMPT_INIT"]):
        print(f"{i:4d}| {ln[:120]}")