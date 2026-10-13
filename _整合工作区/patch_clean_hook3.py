import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 精确检查：_run_batch_mesh 函数体里有没有调用
import re
m = re.search(r"def _run_batch_mesh\(.*?(?=\n\ndef |\Z)", text, re.DOTALL)
if not m:
    print("[FAIL] 找不到 _run_batch_mesh")
    raise SystemExit(1)

body = m.group(0)
if "_clean_old_named_files(out_dir)" in body:
    print("[SKIP] _run_batch_mesh 内已有调用")
    raise SystemExit(0)

# 用 sess["_is_serial_review"] = is_serial_review 作为锚点
OLD = '''    sess["_is_serial_review"] = is_serial_review
    _mode_p = '''
NEW = '''    sess["_is_serial_review"] = is_serial_review

    # ── 清理旧命名文件（防残留干扰）──
    _clean_old_named_files(out_dir)

    _mode_p = '''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_clean_hook3")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已插入清理调用（精确锚点）")
else:
    print("[FAIL] 找不到精确锚点")
    print("附近代码：")
    print(text[max(0, text.find("sess[\"_is_serial_review\"]")-200):text.find("sess[\"_is_serial_review\"]")+300])
