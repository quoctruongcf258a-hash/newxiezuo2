import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_clean_old_named_files(out_dir)" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

# 在 sess["_is_serial_review"] = is_serial_review 之后插入清理调用
OLD = '''    sess["_is_serial_produce"] = is_serial_produce
    sess["_is_serial_review"] = is_serial_review'''

NEW = '''    sess["_is_serial_produce"] = is_serial_produce
    sess["_is_serial_review"] = is_serial_review

    # ── 清理旧命名文件（防残留干扰）──
    _clean_old_named_files(out_dir)'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_clean_hook2")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已在 _run_batch_mesh 插入 _clean_old_named_files(out_dir)")
else:
    print("[FAIL] 找不到锚点")
