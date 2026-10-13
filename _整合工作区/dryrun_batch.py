import subprocess
from pathlib import Path

WORKDIR = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
PY = str(WORKDIR.parent / ".venv" / "Scripts" / "python.exe")

print("="*60)
print("跑 W0_细纲分析（dry-run）")
print("="*60)
r = subprocess.run([PY, "orchestrator.py", "--program", "写作", "--phase", "W0_细纲分析", "--dry-run"],
                    cwd=str(WORKDIR), capture_output=True)
stdout = r.stdout.decode("utf-8", errors="ignore")
stderr = r.stderr.decode("utf-8", errors="ignore")
for ln in stdout.splitlines():
    if any(k in ln for k in ["[split]", "[产出校验]", "批量", "主", "兜底", "✓", "⛔", "失败记录"]):
        print(f"  {ln}")
if stderr.strip():
    print("STDERR:", stderr[:500])
