from pathlib import Path
import re

print("=" * 70)
print("① tasks.py 所有 write_text 调用")
print("=" * 70)
p = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = p.read_text(encoding="utf-8", errors="ignore")
for i, ln in enumerate(text.splitlines(), 1):
    if "write_text" in ln or "open(" in ln or "codecs" in ln:
        print(f"  {i:4d}| {ln.strip()}")

print()
print("=" * 70)
print("② orchestrator.py 所有 write_text 调用（前 30 个）")
print("=" * 70)
p2 = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text2 = p2.read_text(encoding="utf-8", errors="ignore")
cnt = 0
for i, ln in enumerate(text2.splitlines(), 1):
    if "write_text" in ln:
        print(f"  {i:4d}| {ln.strip()[:120]}")
        cnt += 1
        if cnt >= 30:
            break

print()
print("=" * 70)
print("③ 检查 _write_task_file 的当前实现")
print("=" * 70)
m = re.search(r"def _write_task_file\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if m:
    print(m.group(0))

print()
print("=" * 70)
print("④ 检查生成乱码的任务文件")
print("=" * 70)
task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
for f in sorted(task_dir.glob("*.md"))[-5:]:
    # 尝试用 utf-8 读
    try:
        txt = f.read_text(encoding="utf-8")
        is_utf8_ok = "任务" in txt or "你的任务" in txt
        print(f"  {f.name}")
        print(f"    UTF-8 读取：{'✅ 正常' if is_utf8_ok else '❌ 乱码'}")
    except Exception as e:
        print(f"  {f.name}: UTF-8 读失败 {e}")

    # 尝试用 GBK 读
    try:
        txt_gbk = f.read_bytes().decode("gbk", errors="replace")
        is_gbk_ok = "任务" in txt_gbk or "你的任务" in txt_gbk
        print(f"    GBK 读取：{'✅ 正常' if is_gbk_ok else '❌ 乱码'}")
    except Exception as e:
        print(f"    GBK 读失败 {e}")
