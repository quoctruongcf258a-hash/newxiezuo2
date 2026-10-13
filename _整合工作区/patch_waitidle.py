from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

old = "wait_idle(_real, timeout=30, poll=2)"
new = "wait_idle(_real, timeout=180, poll=5)"
cnt = text.count(old)
text = text.replace(old, new)
TARGET.write_text(text, encoding="utf-8")
print(f"已替换 {cnt} 处 wait_idle timeout 30 → 180")
