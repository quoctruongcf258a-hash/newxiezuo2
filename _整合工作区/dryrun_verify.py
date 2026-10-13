import subprocess
from pathlib import Path

WORKDIR = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
PY = str(WORKDIR.parent / ".venv" / "Scripts" / "python.exe")

for phase in ["简短细纲规划", "细纲", "前30章落地章纲"]:
    print(f"\n{'='*60}\n跑 {phase}\n{'='*60}\n")
    r = subprocess.run([PY, "orchestrator.py", "--program", "规划", "--phase", phase, "--dry-run"],
                        cwd=str(WORKDIR), capture_output=True)
    stdout = r.stdout.decode("utf-8", errors="ignore")
    stderr = r.stderr.decode("utf-8", errors="ignore")
    for line in stdout.splitlines():
        if any(k in line for k in ["[split]", "[产出校验]", "(dry-run)"]):
            print(f"  {line}")
    if stderr.strip():
        print("STDERR:", stderr[:300])
