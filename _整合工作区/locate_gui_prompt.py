from pathlib import Path
import re

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = target.read_text(encoding="utf-8")

# 找 "启动或聚焦" 出现在哪
print("=== 代码里含「启动或聚焦」的位置 ===")
for i, ln in enumerate(text.splitlines()):
    if "启动或聚焦" in ln:
        print(f"  {i+1:4d}| {ln.strip()}")

print()
print("=== 代码里含「只执行以上步骤」的位置 ===")
for i, ln in enumerate(text.splitlines()):
    if "只执行以上步骤" in ln:
        print(f"  {i+1:4d}| {ln.strip()}")

# 找 _do_produce_batch 里 build_task 的实现
print()
print("=== _do_produce_batch 的 build_task ===")
m = re.search(r"def _do_produce_batch\(.*?(?=\n\ndef |\n\n# |\Z)", text, re.DOTALL)
if m:
    body = m.group(0)
    # 打印 build_task 定义部分
    i = body.find("def build_task")
    if i >= 0:
        print(body[i:i+600])
