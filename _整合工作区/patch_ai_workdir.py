import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

changed = 0

# ── 改 1：_build_batch_prompt 输出路径改为 <versions>/<ai>/<item>.md ──
OLD1 = '''    lines = [f"【本环节需生成的完整文件清单（共 {len(expected)} 个，一个都不能漏）】"]
    paths = []
    versions_dir = Path(out_dir) / "versions"
    for item_key, item_data in expected:
        safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
        out_path = versions_dir / f"{chunk_id}__{ai_key}__{safe}.md"
        paths.append((item_key, out_path))
        lines.append(f"  · {item_key}   →   {out_path}")'''

NEW1 = '''    lines = [f"【本环节需生成的完整文件清单（共 {len(expected)} 个，一个都不能漏）】"]
    paths = []
    ai_dir = Path(out_dir) / "versions" / ai_key   # ← 每个 AI 独立目录
    for item_key, item_data in expected:
        safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
        out_path = ai_dir / f"{safe}.md"
        paths.append((item_key, out_path))
        lines.append(f"  · {item_key}   →   {out_path}")'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 改1：_build_batch_prompt 用 <versions>/<ai>/<item>.md")
    changed += 1
else:
    print("[FAIL] 改1 找不到锚点")

# ── 改 2：_do_produce_batch 里 _versions_dir 定义 ──
OLD2 = '''    _versions_dir = Path(out_dir) / "versions"
    _versions_dir.mkdir(parents=True, exist_ok=True)'''

NEW2 = '''    _versions_dir = Path(out_dir) / "versions"
    _versions_dir.mkdir(parents=True, exist_ok=True)
    # 为每个参与的 AI 创建独立目录
    _all_ai_keys = [app["key"]] + [p["key"] for p in (sess.get("participants") or []) if p["key"] != app["key"]]
    for _k in _all_ai_keys:
        (_versions_dir / _k).mkdir(parents=True, exist_ok=True)'''

# 只替换 _do_produce_batch 里的第一次出现
idx_batch = text.find("def _do_produce_batch")
if idx_batch > 0:
    # 在该函数范围内找
    sub = text[idx_batch:]
    if OLD2 in sub:
        sub_new = sub.replace(OLD2, NEW2, 1)
        text = text[:idx_batch] + sub_new
        print("[OK] 改2：_do_produce_batch 创建各 AI 目录")
        changed += 1
    else:
        print("[FAIL] 改2 找不到锚点（在 _do_produce_batch 内）")
else:
    print("[FAIL] 改2 找不到 _do_produce_batch")

# ── 改 3：verify_fn 改为检查 <versions>/<ai>/<item>.md ──
OLD3 = '''    _chunk_prefix = chunk_id or "batch"

    def verify_fn(ai_key_override=None):
        _ai = ai_key_override or primary_key
        missing = 0
        for item_key, _ in expected:
            safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
            p = _versions_dir / f"{_chunk_prefix}__{_ai}__{safe}.md"
            if not (p.exists() and p.stat().st_size >= 100):
                missing += 1
        total = len(expected)
        ok = (missing == 0)
        return ok, f"{total - missing}/{total}"'''

NEW3 = '''    def verify_fn(ai_key_override=None):
        _ai = ai_key_override or primary_key
        ai_dir = _versions_dir / _ai
        missing = 0
        for item_key, _ in expected:
            safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
            p = ai_dir / f"{safe}.md"
            if not (p.exists() and p.stat().st_size >= 100):
                missing += 1
        total = len(expected)
        ok = (missing == 0)
        return ok, f"{total - missing}/{total}"'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 改3：verify_fn 检查 <versions>/<ai>/<item>.md")
    changed += 1
else:
    print("[FAIL] 改3 找不到锚点")

# ── 改 4：成功返回的路径改为 <versions>/<ai>/<item>.md（2 处）──
OLD4 = '''                out_files = []
                for item_key, _ in expected:
                    safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                    p = _versions_dir / f"{_chunk_prefix}__{ai_key}__{safe}.md"
                    out_files.append(p)
                return out_files'''

NEW4 = '''                out_files = []
                ai_dir = _versions_dir / ai_key
                for item_key, _ in expected:
                    safe = str(item_key).replace("/", "_").replace("\\\\", "_").replace(":", "_").strip()[:40]
                    p = ai_dir / f"{safe}.md"
                    out_files.append(p)
                return out_files'''

cnt4 = text.count(OLD4)
if cnt4 > 0:
    text = text.replace(OLD4, NEW4)
    print(f"[OK] 改4：成功返回路径改目录式（{cnt4} 处）")
    changed += 1
else:
    print("[FAIL] 改4 找不到锚点")

# 写回
if changed >= 3:
    bak = TARGET.with_suffix(".py.bak_ai_workdir")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回（{changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处，未写回")
