# test_quest_file.py — 给 QUEST 发一条「读文件」短指令，看它能否读懂
import sys, time
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import send, capture_with_meta
from pathlib import Path

# 1. 写测试文件
test_file = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_test_quest.txt")
test_file.write_text(
    "这是一份测试文件。\n"
    "请把下面这行字原样读出来并回复，不要多说别的：\n"
    "【QUEST文件读取测试成功】\n",
    encoding="utf-8",
)
print(f"测试文件: {test_file}")
print(f"文件内容: {test_file.read_text(encoding='utf-8')}")
print()

# 2. 发短指令
msg = f"请读取文件 {test_file} 的全部内容，按其中的要求执行。"
print(f"发送指令: {msg}")
print()

r = send("QUEST", msg)
print(f"发送返回: {r}")
print()
print("等待 15 秒让 QUEST 回复...")
time.sleep(15)

# 3. 抓回复
meta = capture_with_meta("QUEST")
print(f"抓取结果: n={meta.get('n')}, text 长度={len(meta.get('text',''))}")
print()
print("=== QUEST 回复内容 ===")
print(meta.get("text", "(空)"))