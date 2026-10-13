# fix_tasks_label.py — 安全地把 "本次补强要求" 改成 "输出格式要求"
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")


def main():
    print("=" * 60)
    print("fix_tasks_label")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    # 只替换引号里的文字，不加任何注释
    old = '"本次补强要求"'
    new = '"输出格式要求"'

    if old not in text:
        if new in text:
            print("[跳过] 已改过")
            return
        print("[失败] 找不到『本次补强要求』")
        return

    bak = TARGET.with_suffix(".py.bak_label2")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    n = text.count(old)
    text = text.replace(old, new)
    TARGET.write_text(text, encoding="utf-8")
    print(f"✔ 已把 {n} 处『本次补强要求』改为『输出格式要求』")
    print(f"✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()