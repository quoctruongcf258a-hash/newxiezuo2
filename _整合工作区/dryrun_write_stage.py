import subprocess
from pathlib import Path

WORKDIR = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
PY = str(WORKDIR.parent / ".venv" / "Scripts" / "python.exe")

for phase in ["W0_细纲分析", "W1_章前对齐卡", "W2_分布", "W3_正文", "W4_章内节奏自检"]:
    print(f"\n{'='*60}\n跑 {phase}\n{'='*60}\n")
    r = subprocess.run([PY, "orchestrator.py", "--program", "写作", "--phase", phase, "--dry-run"],
                        cwd=str(WORKDIR), capture_output=True)
    stdout = r.stdout.decode("utf-8", errors="ignore")
    stderr = r.stderr.decode("utf-8", errors="ignore")
    lines = [ln for ln in stdout.splitlines() if any(k in ln for k in ["[split]", "[产出校验]", "(dry-run)"])]
    for ln in lines[:8]:
        print(f"  {ln}")
    if len(lines) > 8:
        print(f"  ... (还有 {len(lines)-8} 行)")
        print(f"  {lines[-1]}")
    if stderr.strip():
        print("STDERR:", stderr[:300])
