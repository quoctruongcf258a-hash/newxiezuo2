# fix_capture_wait.py — do_review/do_produce 的 capture 等待从 60 秒加到 180 秒
import shutil
from pathlib import Path

T = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = T.read_text(encoding="utf-8")
changed = 0

# do_review 里的 for _try in range(6)
OLD = "for _try in range(6):                # 最多等 60 秒"
NEW = "for _try in range(18):               # 最多等 180 秒"
if OLD in text:
    text = text.replace(OLD, NEW, 1)
    changed += 1
    print("✔ do_review 等待 60→180 秒")
else:
    # 试试别的写法
    OLD2 = "for _try in range(6):"
    if OLD2 in text:
        text = text.replace(OLD2, "for _try in range(18):  # 180 秒", 1)
        changed += 1
        print("✔ 找到 range(6) 改成 range(18)")
    else:
        print("✗ 找不到 range(6)")

# do_produce 里的 for _try in range(6)
if "for _try in range(6):" in text:
    text = text.replace("for _try in range(6):", "for _try in range(18):  # 180 秒", 1)
    changed += 1
    print("✔ do_produce 等待也改了")

# do_merge 也加 capture 兜底（现在只靠 wait_file）
if "do_merge" in text and "_cap(app[" not in text[text.find("def do_merge"):text.find("def do_merge")+2000]:
    print("提示：do_merge 还没有 capture 兜底，拼接可能也失败")

if changed:
    bak = T.with_suffix(".py.bak_capwait")
    if not bak.exists():
        shutil.copy(T, bak)
        print(f"已备份：{bak.name}")
    T.write_text(text, encoding="utf-8")
    print(f"✔ 共改 {changed} 处")
else:
    print("没有改动")