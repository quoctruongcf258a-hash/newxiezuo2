from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# ── 1. 检查函数是否在 __main__ 之后 ──
if "_do_produce_renwu" not in text:
    print("[FAIL] 找不到 _do_produce_renwu，无法修复")
    raise SystemExit(1)

i_main = text.find('\nif __name__ == "__main__":')
if i_main < 0:
    print("[FAIL] 找不到 if __name__ == '__main__'")
    raise SystemExit(1)

i_func = text.find("def _do_produce_renwu(")
if i_func < 0:
    print("[FAIL] 找不到 def _do_produce_renwu")
    raise SystemExit(1)

if i_func < i_main:
    print("[SKIP] 函数已经在 __main__ 之前，无需修复")
    raise SystemExit(0)

print(f"[INFO] 函数位置：第 {text[:i_func].count(chr(10))+1} 行")
print(f"[INFO] __main__ 位置：第 {text[:i_main].count(chr(10))+1} 行")
print("[INFO] 需要把函数挪到 __main__ 之前")

# ── 2. 提取函数块 ──
# 从 def _do_produce_renwu 开始，到文件末尾（如果后面没有别的 def）
# 更保守：找到下一个顶层 def 或文件末尾
tail = text[i_func:]
# 检查函数结尾是否有别的内容
lines_tail = tail.splitlines()
# 通常函数是文件最后一段，直接整个 tail 作为函数体
func_block = tail.rstrip() + "\n"

# ── 3. 删除原函数 ──
new_text = text[:i_func].rstrip() + "\n"

# ── 4. 在 __main__ 之前插入 ──
i_main2 = new_text.find('\nif __name__ == "__main__":')
if i_main2 < 0:
    print("[FAIL] 重新定位 __main__ 失败")
    raise SystemExit(1)

new_text = (
    new_text[:i_main2].rstrip()
    + "\n\n\n"
    + func_block
    + "\n\n"
    + new_text[i_main2:].lstrip("\n")
)

# ── 5. 写回 ──
TARGET.write_text(new_text, encoding="utf-8")
print(f"\n[OK] 已修复：_do_produce_renwu 挪到 __main__ 之前")
