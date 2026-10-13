# split_renwu.py — do_produce 之后自动拆「人物设计」为 N 个文件
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")

# 1. 在 do_produce 之后插入 _split_renwu 函数
OLD_DO_PRODUCE_TAIL = '''    ok = run_task(agent, task, dry, title=f"产出 | {app['label']} | {label} | {chunk_label}", app=app)
    if ok and not dry:
        wait_file(out)
    return out


def do_review(agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
'''

NEW_DO_PRODUCE_TAIL = '''    ok = run_task(agent, task, dry, title=f"产出 | {app['label']} | {label} | {chunk_label}", app=app)
    if ok and not dry:
        wait_file(out)
        # 人物设计环节：拆成 N 个文件（每人一份）
        if phase_cfg.get("key") == "人物设计":
            try:
                _split_renwu(out, app["key"])
            except Exception as _e:
                print(f"   [拆分失败] {_e}")
    return out


def _split_renwu(main_path, ai_key):
    """把人物设计合并文件按「# 人物设计：<名字>」拆成 N 个文件。"""
    import re
    text = read_text(main_path)
    if not text.strip():
        return
    parts = re.split(r"^#\\s*人物设计[：:]\\s*", text, flags=re.MULTILINE)
    if len(parts) < 2:
        print("   [拆分] 未找到人物标记，保留原文件")
        return
    parent = Path(main_path).parent
    n = 0
    for seg in parts[1:]:
        lines = seg.splitlines()
        if not lines:
            continue
        name = lines[0].strip()
        if not name:
            continue
        safe = name.replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
        body = "\\n".join(lines[1:]).strip()
        out = parent / f"{safe}__{ai_key}.md"
        write_text(out, f"# 人物设计：{name}\\n{body}\\n")
        n += 1
    print(f"   [拆分] 人物设计 → {n} 个文件（{parent}）")


def do_review(agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
'''

text = TARGET.read_text(encoding="utf-8")

if "_split_renwu" in text:
    print("已改过")
elif OLD_DO_PRODUCE_TAIL not in text:
    print("找不到 do_produce 尾部锚点，看实际代码")
else:
    bak = TARGET.with_suffix(".py.bak_split")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD_DO_PRODUCE_TAIL, NEW_DO_PRODUCE_TAIL, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已加 _split_renwu + do_produce 调用")