from pathlib import Path

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = target.read_text(encoding="utf-8")

i_func = text.find("def _do_produce_renwu(")
i_main = text.find('\nif __name__ == "__main__":')

print(f"_do_produce_renwu 位置：第 {text[:i_func].count(chr(10))+1} 行")
print(f"if __name__ 位置：第 {text[:i_main].count(chr(10))+1} 行")
print(f"\n函数在 __main__ 之前：{'是 [OK]' if i_func < i_main else '否 [FAIL]'}")

# 打印文件末尾 10 行
print("\n=== 文件末尾 10 行 ===")
for ln in text.splitlines()[-10:]:
    print(f"  | {ln}")
