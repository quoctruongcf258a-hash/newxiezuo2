from pathlib import Path
import shutil

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_idle60")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print("已备份：", bak.name)

old1 = "if _idle_count >= 3:"
new1 = "if _idle_count >= 12:"
cnt1 = text.count(old1)
text = text.replace(old1, new1)

old2 = "wait_idle(_real, timeout=30, poll=2)"
new2 = "wait_idle(_real, timeout=180, poll=5)"
cnt2 = text.count(old2)
text = text.replace(old2, new2)

TARGET.write_text(text, encoding="utf-8")
print(f"改动1：_idle_count >= 3 → >= 12，共 {cnt1} 处")
print(f"改动2：wait_idle timeout 30→180，共 {cnt2} 处")
