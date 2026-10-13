lines = open(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py", encoding="utf-8").readlines()
for i, ln in enumerate(lines):
    if "def phase_input" in ln:
        print(f"--- 第{i+1}行起 ---")
        print("".join(lines[i:i+35]))
        break