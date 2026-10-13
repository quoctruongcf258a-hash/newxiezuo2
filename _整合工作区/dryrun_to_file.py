# dryrun_to_file.py — 直接在 Python 里捕获子进程输出字节，绕过 PowerShell 编码
import subprocess
from pathlib import Path

# ── 工作目录：orchestrator.py 所在目录（保持不变，依赖相对路径的 rules/）──
WORKDIR = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
PY = str(WORKDIR.parent / ".venv" / "Scripts" / "python.exe")

# ── 输出目录：统一到 _整合工作区\_scratch\ ──
OUTDIR = Path(r"F:\赛马23环整合工作室\_整合工作区\_scratch")
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / "_dryrun.txt"

args = [
    PY,
    "orchestrator.py",
    "--program", "规划",
    "--phase", "一句话故事",
    "--dry-run",
]

print(f"工作目录：{WORKDIR}")
print(f"输出目录：{OUTDIR}")
print(f"运行：{args}")
r = subprocess.run(args, cwd=str(WORKDIR), capture_output=True)

# 直接写原始字节（Python 的 stdout 是 UTF-8 字节）
OUT.write_bytes(r.stdout + b"\n===== STDERR =====\n" + r.stderr)
print(f"[OK] 已写出：{OUT}")
print(f"  stdout 字节数：{len(r.stdout)}")
print(f"  stderr 字节数：{len(r.stderr)}")
print()
print("打开看：")
print(f'  code "{OUT}"')
