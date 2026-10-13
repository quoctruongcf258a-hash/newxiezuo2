# fix_mkdir.py — do_review / do_merge 落盘前创建父目录
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")
changed = []

# 1) do_review：out 后面加 mkdir
OLD1 = '''    out = Path(out_dir) / "reviews" / f"{chunk_id}__{Path(target_path).stem}__{app['key']}.json"
    label = f"{program} › {phase_cfg['key']}"'''
NEW1 = '''    out = Path(out_dir) / "reviews" / f"{chunk_id}__{Path(target_path).stem}__{app['key']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)   # 保证 reviews 目录存在
    label = f"{program} › {phase_cfg['key']}"'''
if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    changed.append("do_review mkdir")

# 2) do_merge：out 后面加 mkdir
OLD2 = '''    out = Path(out_dir) / "merged" / f"{chunk_id}.md"
    task = tasks_mod.build_merge_task(app, compose_prompt("PROMPT_MERGE.md", program),'''
NEW2 = '''    out = Path(out_dir) / "merged" / f"{chunk_id}.md"
    out.parent.mkdir(parents=True, exist_ok=True)   # 保证 merged 目录存在
    task = tasks_mod.build_merge_task(app, compose_prompt("PROMPT_MERGE.md", program),'''
if OLD2 in text:
    text = text.replace(OLD2, NEW2, 1)
    changed.append("do_merge mkdir")

# 3) do_produce：也加（保险）
OLD3 = '''    out = Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"
    label = f"{program} › {phase_cfg['key']}"'''
NEW3 = '''    out = Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"
    out.parent.mkdir(parents=True, exist_ok=True)   # 保证 versions 目录存在
    label = f"{program} › {phase_cfg['key']}"'''
if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    changed.append("do_produce mkdir")

if changed:
    bak = TARGET.with_suffix(".py.bak_mkdir")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    for c in changed:
        print(f"✔ {c}")
else:
    print("没有改动（可能都改过或锚点不匹配）")