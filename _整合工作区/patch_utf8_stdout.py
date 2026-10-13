# patch_utf8_stdout.py — 让 orchestrator.py 输出永远用 UTF-8
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")


def main():
    print("=" * 60)
    print("patch_utf8_stdout")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_UTF8_STDOUT_FIX" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_utf8")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 锚点：import 块之后的第一行有效代码之前插入
    # 用 'HERE = Path(__file__).resolve().parent' 作为锚点
    anchor = "HERE = Path(__file__).resolve().parent\n"
    if anchor not in text:
        print("[失败] 找不到锚点 HERE = Path(__file__).resolve().parent")
        return

    insert = anchor + '''

# _UTF8_STDOUT_FIX：强制 stdout/stderr 用 UTF-8，避免 GBK 编码崩溃
try:
    import sys as _sys
    if hasattr(_sys.stdout, "reconfigure"):
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(_sys.stderr, "reconfigure"):
        _sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
'''

    text = text.replace(anchor, insert, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已在 orchestrator.py 顶部插入 UTF-8 stdout 补丁")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()