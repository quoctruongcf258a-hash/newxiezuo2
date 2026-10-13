import subprocess
from pathlib import Path

WORKDIR = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
PY = str(WORKDIR.parent / ".venv" / "Scripts" / "python.exe")

for phase in ["W0_细纲分析", "W1_章前对齐卡"]:
    print(f"\n{'='*60}\n跑 {phase}\n{'='*60}\n")
    r = subprocess.run([PY, "orchestrator.py", "--program", "写作", "--phase", phase, "--dry-run"],
                        cwd=str(WORKDIR), capture_output=True)
    stdout = r.stdout.decode("utf-8", errors="ignore")
    stderr = r.stderr.decode("utf-8", errors="ignore")
    # 只看含"追加按章上游"和"章1/章2/章5"相关的行
    for ln in stdout.splitlines():
        if any(k in ln for k in ["追加按章上游", "[产出校验]"]):
            print(f"  {ln}")
    if stderr.strip():
        print("STDERR:", stderr[:300])
