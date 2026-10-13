import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_clean_old_named_files(out_dir)" in text and "# ── 清理旧命名" in text:
    print("[SKIP] 已存在")
    raise SystemExit(0)

# 精确匹配 _run_batch_mesh 里的 versions_dir 定义
OLD = '''    from concurrent.futures import ThreadPoolExecutor, as_completed

    versions_dir = Path(out_dir) / "versions"'''

NEW = '''    from concurrent.futures import ThreadPoolExecutor, as_completed

    # ── 清理旧命名文件（防残留干扰）──
    _clean_old_named_files(out_dir)

    versions_dir = Path(out_dir) / "versions"'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    bak = TARGET.with_suffix(".py.bak_clean_hook")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已在 _run_batch_mesh 开头插入清理调用")
else:
    print("[FAIL] 找不到锚点")
    # 打印附近代码
    i = text.find("def _run_batch_mesh")
    if i >= 0:
        print("\n附近代码：")
        print(text[i:i+600])
