lines = open(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py", encoding="utf-8").readlines()
for i, ln in enumerate(lines):
    if "def _save_block" in ln:
        print(f"--- 第{i+1}行起 ---")
        print("".join(lines[i:i+20]))
        break