# patch_drop_ai_policy.py — 去掉平台硬约束里的"AI 政策"行
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")


def main():
    print("=" * 60)
    print("patch_drop_ai_policy")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_NO_AI_POLICY" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_noaipolicy")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # 找 platform_block 里加 AI 政策那几行
    old = '''    if p.get("reviewRedlines", {}).get("aiPolicy", {}).get("平台立场"):
        parts.append(f"  · AI 政策：{p['reviewRedlines']['aiPolicy']['平台立场']}")
'''
    new = '''    # _NO_AI_POLICY：AI 政策行已去掉（用户要求）
'''

    if old not in text:
        print("[失败] 找不到 AI 政策那一行")
        print("       可能格式已变，请发我 platform_block 函数内容")
        return
    text = text.replace(old, new, 1)
    print("✔ 已去掉『AI 政策』行")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()