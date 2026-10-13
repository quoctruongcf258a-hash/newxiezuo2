import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''    fp.write_text(body, encoding="utf-8")
    return fp'''

NEW = '''    # 用 UTF-8 BOM 保存——让 Windows 下的编辑器/AI 自动识别为 UTF-8
    # （不靠 AI 自己猜编码，防乱码）
    fp.write_bytes(b"\\xef\\xbb\\xbf" + body.encode("utf-8"))
    return fp'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_bom")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已改为 UTF-8 with BOM")
else:
    print("[FAIL] 找不到锚点")
