import subprocess
from pathlib import Path

WORKDIR = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
PY = str(WORKDIR.parent / ".venv" / "Scripts" / "python.exe")

for phase in ["Q1_逻辑设定一致", "Q2_平台合规", "Q3_爽点节奏", "Q4_文风格式回查",
              "Q5_质检汇总", "Q7_上架前低级错误检查", "Q9_推演下一章"]:
    print(f"\n{'='*60}\n跑 {phase}\n{'='*60}")
    r = subprocess.run([PY, "orchestrator.py", "--program", "质检", "--phase", phase, "--dry-run"],
                        cwd=str(WORKDIR), capture_output=True)
    stdout = r.stdout.decode("utf-8", errors="ignore")
    stderr = r.stderr.decode("utf-8", errors="ignore")
    for ln in stdout.splitlines():
        if any(k in ln for k in ["[split]", "[产出校验]", "追加按章上游"]):
            print(f"  {ln}")
    if stderr.strip():
        print("STDERR:", stderr[:300])
