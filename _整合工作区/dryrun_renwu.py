# dryrun_renwu.py — 单独跑一次人物设计环节的 dry-run
import subprocess
from pathlib import Path

WORKDIR = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
PY = str(WORKDIR.parent / ".venv" / "Scripts" / "python.exe")
OUTDIR = Path(r"F:\赛马23环整合工作室\_整合工作区\_scratch")
OUTDIR.mkdir(parents=True, exist_ok=True)

args = [
    PY,
    "orchestrator.py",
    "--program", "规划",
    "--phase", "人物设计",
    "--dry-run",
]

print(f"运行：{args}\n")
r = subprocess.run(args, cwd=str(WORKDIR), capture_output=True)

out_file = OUTDIR / "_dryrun_renwu.txt"
out_file.write_bytes(r.stdout + b"\n===== STDERR =====\n" + r.stderr)
print(f"[OK] 已写出：{out_file}")
print(f"  stdout {len(r.stdout)}B / stderr {len(r.stderr)}B\n")

# 直接打印 stdout 最后 60 行
print("=== stdout 末尾 60 行 ===")
lines = r.stdout.decode("utf-8", errors="ignore").splitlines()
for ln in lines[-60:]:
    print(f"  {ln}")
