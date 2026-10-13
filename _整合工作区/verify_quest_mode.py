# verify_quest_mode.py — 确认 QUEST 全环节走文件模式
import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import tasks

print("=" * 60)
print("1) FILE_MODE_AIS 配置")
print("=" * 60)
print(f"FILE_MODE_AIS = {tasks.FILE_MODE_AIS}")
print(f"QUEST 在里面: {'QUEST' in tasks.FILE_MODE_AIS}")
print()

print("=" * 60)
print("2) 三个任务模板是否走文件模式")
print("=" * 60)
app_quest = {"key": "QUEST", "label": "QUEST", "类型": "electron"}
app_other = {"key": "Doubao", "label": "Doubao", "类型": "electron"}

# 产出
r1 = tasks.build_produce_task(app_quest, "测试", "材料", "F:\\out.md", "规划", "块1")
print(f"产出(QUEST) → 文件模式: {'请读取下面这个文件' in r1}")
r1b = tasks.build_produce_task(app_other, "测试", "材料", "F:\\out.md", "规划", "块1")
print(f"产出(Doubao) → 粘贴模式: {'按 Ctrl+V' in r1b}")
print()

# 盲审
r2 = tasks.build_review_task(app_quest, "测试", "待审产出", "F:\\out.json", "规划", "块1")
print(f"盲审(QUEST) → 文件模式: {'请读取下面这个文件' in r2}")
r2b = tasks.build_review_task(app_other, "测试", "待审产出", "F:\\out.json", "规划", "块1")
print(f"盲审(Doubao) → 粘贴模式: {'按 Ctrl+V' in r2b}")
print()

# 拼接
r3 = tasks.build_merge_task(app_quest, "测试", "版本", "盲审", "F:\\out.md", "规划", "块1")
print(f"拼接(QUEST) → 文件模式: {'请读取下面这个文件' in r3}")
r3b = tasks.build_merge_task(app_other, "测试", "版本", "盲审", "F:\\out.md", "规划", "块1")
print(f"拼接(Doubao) → 粘贴模式: {'按 Ctrl+V' in r3b}")
print()

print("=" * 60)
print("3) 三个任务里都有文件路径")
print("=" * 60)
import re
for name, text in [("产出", r1), ("盲审", r2), ("拼接", r3)]:
    m = re.search(r'task__[^\s。]+\.md', text)
    print(f"{name}: {m.group(0) if m else '✗ 找不到路径'}")