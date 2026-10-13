import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_rbm_serial")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

# 精确匹配真实代码的锚点
OLD = '''    from concurrent.futures import ThreadPoolExecutor, as_completed

    versions_dir = Path(out_dir) / "versions"
'''

NEW = '''    from concurrent.futures import ThreadPoolExecutor, as_completed

    # ── 串行/赛马判定 ──
    #   writers 数 = 1 → 串行（失败换人）
    #   writers 数 >= 2 → 赛马（失败淘汰，不补）
    is_serial_produce = (len(writers) == 1)
    is_serial_review = (len(reviewers) <= 1)
    sess["_is_serial_produce"] = is_serial_produce
    sess["_is_serial_review"] = is_serial_review
    _mode_p = "串行（失败换人）" if is_serial_produce else f"赛马（{len(writers)} AI 竞争）"
    print(f"   [模式] 产出：{_mode_p}")
    if reviewers:
        _mode_r = "串行（失败换人）" if is_serial_review else f"赛马（{len(reviewers)} AI 盲审）"
        print(f"   [模式] 盲审：{_mode_r}")

    versions_dir = Path(out_dir) / "versions"
'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] 已插入串行/赛马判定")
else:
    print("[FAIL] 找不到锚点")
    # 打印 _run_batch_mesh 附近代码
    i = text.find("def _run_batch_mesh")
    if i >= 0:
        print("\n实际代码片段：")
        print(text[i:i+500])
