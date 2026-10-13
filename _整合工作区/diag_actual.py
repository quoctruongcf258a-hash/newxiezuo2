from pathlib import Path

T1 = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text1 = T1.read_text(encoding="utf-8")

print("=" * 70)
print("orchestrator.py 现有辅助函数")
print("=" * 70)
for name in ["_get_ai_steps", "_incr_ai_steps", "_scan_total_progress",
             "_get_or_assign_step", "_reset_steps_for_project",
             "_scan_progress", "_clean_old_named_files"]:
    print(f"  {name}: {'✅' if name in text1 else '❌'}")

print()
print("=" * 70)
print("tasks.py 里 _step_no / _KIND_STEP / _get_current_step 现状")
print("=" * 70)
T2 = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text2 = T2.read_text(encoding="utf-8")
for kw in ["_KIND_STEP", "_get_current_step", "_step_no", "_get_or_assign_step"]:
    cnt = text2.count(kw)
    print(f"  {kw}: {cnt} 次")

# 打印 _KIND_STEP 附近
i = text2.find("_KIND_STEP")
if i >= 0:
    print()
    print("_KIND_STEP 附近：")
    print(text2[max(0,i-100):i+300])

i2 = text2.find("_step_no")
if i2 >= 0:
    print()
    print("_step_no 附近：")
    print(text2[max(0,i2-300):i2+200])

# 找 orchestrator 里可以用的锚点
print()
print("=" * 70)
print("orchestrator.py 里可用作插入锚点的函数")
print("=" * 70)
import re
for m in re.finditer(r"^def (_\w+)\(", text1, re.MULTILINE):
    name = m.group(1)
    if any(k in name for k in ["step", "progress", "scan", "clean", "wait", "produce", "review"]):
        line_no = text1[:m.start()].count("\n") + 1
        print(f"  {line_no:5d}| def {name}(")
