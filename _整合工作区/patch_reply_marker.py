import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_reply_marker")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# 找到"完成后回复「✅ 已完成」"这一行，改成带标识
OLD = '''    body += "## 执行约束\\n"
    body += "- 直接用你的文件读取能力读「上游资料」里的路径\\n"
    body += "- 直接用你的文件写入能力写到「输出位置」的路径\\n"
    body += "- 不要输出操作步骤、不要问我确认、不要参考其他内容\\n"
    body += "- 完成后回复「✅ 已完成」\\n"'''

NEW = '''    body += "## 执行约束\\n"
    body += "- 直接用你的文件读取能力读「上游资料」里的路径\\n"
    body += "- 直接用你的文件写入能力写到「输出位置」的路径\\n"
    body += "- 不要输出操作步骤、不要问我确认、不要参考其他内容\\n"
    # 回复标识：带 ai_key + 环节名 + 输出文件名，便于肉眼确认哪个任务完成
    _out_name = Path(out_path).name
    body += f"- 完成后，**必须**回复这一行（一字不改）：\\n"
    body += f"  `✅ [{ai_key}] {phase_label} → {_out_name} 已完成`\\n"
    body += f"- 如果失败，回复 `❌ [{ai_key}] {phase_label} → {_out_name} 失败：<原因>`\\n"'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] 已改任务文件的回复格式")
else:
    print("[FAIL] 找不到锚点")
    # 打印附近代码
    i = text.find("完成后回复")
    if i >= 0:
        print("\n附近代码：")
        print(text[max(0,i-400):i+200])

TARGET.write_text(text, encoding="utf-8")
print(f"\n[OK] 已写回：{TARGET.name}")
