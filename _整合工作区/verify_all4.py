# verify_all4.py — 4 个 AI 全验证是否走文件模式
import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import tasks

print(f"FILE_MODE_AIS = {tasks.FILE_MODE_AIS}")
print()

ais = ["quest", "workbuddy", "doubao", "gemini"]
for k in ais:
    app = {"key": k, "label": k.capitalize(), "类型": "electron"}
    r1 = tasks.build_produce_task(app, "P", "I", "F:\\o.md", "规划", "块1")
    r2 = tasks.build_review_task(app, "P", "T", "F:\\o.json", "规划", "块1")
    r3 = tasks.build_merge_task(app, "P", "V", "R", "F:\\o.md", "规划", "块1")
    fm = "请读取下面这个文件" in r1
    print(f"{k:12s}  文件模式={fm}  produce={fm}  review={'请读取下面这个文件' in r2}  merge={'请读取下面这个文件' in r3}")