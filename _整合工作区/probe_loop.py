# probe_loop.py — 看 orchestrator 的流程控制 / 章循环 / --loop
from pathlib import Path

P = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = P.read_text(encoding="utf-8").splitlines()
text = "\n".join(lines)

print("=" * 30, "main 函数 / argparse", "=" * 30)
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ["argparse", "add_argument", "def main", "__main__",
                              "args.program", "args.chapter", "args.loop"]):
        print(f"{i:4d}| {ln[:130]}")

print()
print("=" * 30, "loop / 章循环 相关", "=" * 30)
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ["loop", "for ch", "chapter in", "range(", "章循环"]):
        print(f"{i:4d}| {ln[:130]}")

print()
print("=" * 30, "程序名列表 / STAGE_MAP / 顺序", "=" * 30)
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ["STAGE_MAP", "PROGRAM_ORDER", "程序顺序", "['规划'",
                              '["规划"', "PROGRAMS ="]):
        print(f"{i:4d}| {ln[:130]}")

print()
print("=" * 30, "文件总行数", "=" * 30)
print(len(lines), "行")