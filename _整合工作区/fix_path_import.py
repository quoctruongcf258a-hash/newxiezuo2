# fix_path_import.py — tasks.py 补 Path import
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

if "from pathlib import Path" in text.split("# 走「读文件」模式")[0]:
    print("已有 Path import")
else:
    # 找第一行 import
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("import ") or ln.startswith("from "):
            lines.insert(i, "from pathlib import Path")
            print(f"已在第 {i+1} 行插入 import")
            break
    else:
        lines.insert(0, "from pathlib import Path")
        print("已在文件头插入 import")
    text = "\n".join(lines)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已保存")