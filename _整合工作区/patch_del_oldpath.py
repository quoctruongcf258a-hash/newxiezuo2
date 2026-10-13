import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_del_oldpath")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

OLD = '''    _read_block += (
        "\\n\\n【本环节输出路径（写到这里才算完成）】"
        f"\\n  {_out_dir / 'versions' / (phase_cfg['key'] + '__<你的名字>.md')}"
        "\\n\\n【完成判定】"
        "\\n  任务完成 = 下列全部满足："
        "\\n    1. 文件已保存到上面「输出路径」"
        "\\n    2. 文件内容非空（≥200 字）"
        "\\n    3. 严格按【输出格式要求】执行"
        "\\n    4. 只输出本块成品，不越界"
    )'''

NEW = '''    # 输出路径已由 _build_batch_prompt 统一给出，这里不再重复（避免矛盾）'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] 已删除 phase_input 里旧的输出路径段")
else:
    print("[WARN] 找不到锚点")

TARGET.write_text(text, encoding="utf-8")
print(f"[OK] 已写回")
