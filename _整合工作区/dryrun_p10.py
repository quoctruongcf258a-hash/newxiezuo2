import subprocess
from pathlib import Path

WORKDIR = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
PY = str(WORKDIR.parent / ".venv" / "Scripts" / "python.exe")

r = subprocess.run([PY, "orchestrator.py", "--program", "规划", "--phase", "分卷结构", "--dry-run"],
                    cwd=str(WORKDIR), capture_output=True)
print(r.stdout.decode("utf-8", errors="ignore"))
print("=== STDERR ===")
print(r.stderr.decode("utf-8", errors="ignore"))
