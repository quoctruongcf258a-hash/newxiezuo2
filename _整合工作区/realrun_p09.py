import subprocess
from pathlib import Path

WORKDIR = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
PY = str(WORKDIR.parent / ".venv" / "Scripts" / "python.exe")

print("=" * 70)
print("真跑 P09 全书结构")
print("=" * 70)
print("预期：4 AI 各生成 1 份 md + 1 份 json")
print()

r = subprocess.run(
    [PY, "orchestrator.py", "--program", "规划", "--phase", "全书结构"],
    cwd=str(WORKDIR), capture_output=False,
)
print(f"\n返回码：{r.returncode}")
