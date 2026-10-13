import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

bak = TARGET.with_suffix(".py.bak_bbp_fix")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

OLD = '''    lines = [f"【本环节需生成的完整文件清单（共 {len(expected)} 个，一个都不能漏）】"]
    paths = []
    versions_dir = Path(out_dir) / "versions"
    for item_key, item_data in expected:
        safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
        out_path = versions_dir / f"{ai_key}__{safe}.md"
        paths.append((item_key, out_path))
        lines.append(f"  · {item_key}   →   {out_path}")'''

NEW = '''    lines = [f"【本环节需生成的完整文件清单（共 {len(expected)} 个，一个都不能漏）】"]
    paths = []
    ai_dir = Path(out_dir) / "versions" / ai_key   # ← 目录隔离
    ai_dir.mkdir(parents=True, exist_ok=True)
    for item_key, item_data in expected:
        safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
        out_path = ai_dir / f"{safe}.md"            # ← 用 item_key 作文件名
        paths.append((item_key, out_path))
        lines.append(f"  · {item_key}   →   {out_path}")'''

if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("[OK] _build_batch_prompt 用目录隔离 + item_key")
else:
    print("[FAIL] 找不到锚点")
    i = text.find("_build_batch_prompt")
    if i >= 0:
        print(text[i:i+800])

TARGET.write_text(text, encoding="utf-8")
print(f"[OK] 已写回")
