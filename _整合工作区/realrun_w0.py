import subprocess
from pathlib import Path

WORKDIR = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
PY = str(WORKDIR.parent / ".venv" / "Scripts" / "python.exe")

print("=" * 70)
print("真跑 W0_细纲分析（3 章 × 4 AI）")
print("=" * 70)

r = subprocess.run(
    [PY, "orchestrator.py", "--program", "写作", "--phase", "W0_细纲分析"],
    cwd=str(WORKDIR),
    capture_output=False,
)
print(f"\n=== 返回码：{r.returncode} ===")
