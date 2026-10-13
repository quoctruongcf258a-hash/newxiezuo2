from pathlib import Path

log = Path(r"F:\赛马23环整合工作室\_整合工作区\_scratch\_dryrun_renwu.txt")
text = log.read_text(encoding="utf-8", errors="ignore")

# 分离 stdout / stderr
if "===== STDERR =====" in text:
    stdout_part, stderr_part = text.split("===== STDERR =====", 1)
else:
    stdout_part, stderr_part = text, "(无 stderr)"

print("=" * 60)
print("📄 STDOUT 全文")
print("=" * 60)
for ln in stdout_part.splitlines():
    print(ln)

print("\n" + "=" * 60)
print("⚠️ STDERR 全文")
print("=" * 60)
for ln in stderr_part.splitlines():
    print(ln)
