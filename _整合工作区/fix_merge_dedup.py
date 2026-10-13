# fix_merge_dedup.py — 拼接者加「最终校验·去重」任务
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''  · 只做「挑选 / 拼接 / 局部重写」，不要顺手通篇改写、不要改动未被点名的段落。

步骤：'''

NEW = '''  · 只做「挑选 / 拼接 / 局部重写」，不要顺手通篇改写、不要改动未被点名的段落。

最终校验·必做（保存之前执行）：
  · 扫描拼合结果，找出重复出现的段落 / 句子 / 设定说明 / 关键词；
  · 同一信息只保留最完整的一份，删除其余重复段落；
  · 精简后输出，让下游环节读到不重复的定稿；
  · 去重只删重复，不要删信息，不要改写未重复的内容。

步骤：'''

if "最终校验·必做（保存之前执行）" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
    i = text.find("只做「挑选 / 拼接 / 局部重写」")
    if i >= 0:
        print(text[i-50:i+200])
else:
    bak = TARGET.with_suffix(".py.bak_mergededup")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 拼接者已加「最终校验·去重」任务")