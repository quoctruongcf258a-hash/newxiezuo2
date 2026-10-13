# fix_chufang.py — 接入「出厂」程序 + 加 --pipeline 顶层循环
import re
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")
changed = []

# 1) STAGE_MAP 加「出厂」
m = re.search(r'(STAGE_MAP\s*=\s*\{)(.*?)(\n\})', text, re.S)
if m:
    body = m.group(2)
    if '"出厂"' not in body:
        if not body.rstrip().endswith(","):
            body = body.rstrip() + ","
        body = body.rstrip() + '\n    "出厂": "05_出厂",'
        text = text[:m.start()] + m.group(1) + body + m.group(3) + text[m.end():]
        changed.append("STAGE_MAP")
else:
    print("✗ 找不到 STAGE_MAP")

# 2) _STAGE_DIR_MAP 加「出厂」
m = re.search(r'(_STAGE_DIR_MAP\s*=\s*\{)(.*?)(\n\})', text, re.S)
if m:
    body = m.group(2)
    if '"出厂"' not in body:
        if not body.rstrip().endswith(","):
            body = body.rstrip() + ","
        body = body.rstrip() + '\n    "出厂": "05_出厂",'
        text = text[:m.start()] + m.group(1) + body + m.group(3) + text[m.end():]
        changed.append("_STAGE_DIR_MAP")
else:
    print("✗ 找不到 _STAGE_DIR_MAP")

# 3) PROGRAM_GATES 加「出厂」
OLD = '''PROGRAM_GATES = {
    "规划": "章纲终审",
    "写作": "正文终审",
    "润色": "润色终审",
    "质检": "成书检验",
}'''
NEW = '''PROGRAM_GATES = {
    "规划": "章纲终审",
    "写作": "正文终审",
    "润色": "润色终审",
    "质检": "成书检验",
    "出厂": "定稿归档",
}'''
if OLD in text:
    text = text.replace(OLD, NEW, 1)
    changed.append("PROGRAM_GATES")

# 4) --program choices 加「出厂」
OLD = 'ap.add_argument("--program", choices=["规划", "写作", "润色", "质检"])'
NEW = 'ap.add_argument("--program", choices=["规划", "写作", "润色", "质检", "出厂"])'
if OLD in text:
    text = text.replace(OLD, NEW, 1)
    changed.append("--program choices")

# 5) 加 --pipeline / --chapters 参数
OLD = '    ap.add_argument("--once", action="store_true", help="每环节只让 1 名 AI 产出（省额度试跑）")'
if OLD in text and "--pipeline" not in text:
    NEW = OLD + '''
    ap.add_argument("--pipeline", action="store_true", help="整章流水线：写作→润色→质检→出厂")
    ap.add_argument("--chapters", default="", help="章范围，如 1-150 / 1,3,5")'''
    text = text.replace(OLD, NEW, 1)
    changed.append("--pipeline/--chapters")

# 6) run_program 里加 fixed 分支
OLD = '''        if ph.get("mode") == "storage":
            _do_storage(cfg, program, chapter, dry)'''
NEW = '''        if ph.get("mode") == "fixed":
            print(f"\\n▶ 环节「{ph['key']}」为【固定流程】，请人工确认。")
            print(f"   说明：{ph.get('desc', '')}")
            continue
        if ph.get("mode") == "storage":
            _do_storage(cfg, program, chapter, dry)'''
if OLD in text:
    text = text.replace(OLD, NEW, 1)
    changed.append("fixed 分支")

# 7) 加 run_pipeline + _parse_chapters 函数
OLD = '''def _chapter_num(chapter):
    try:
        return int(str(chapter).lstrip("0") or "0")
    except Exception:                              # noqa: BLE001
        return 0
'''
if OLD in text and "def run_pipeline" not in text:
    NEW = '''def run_pipeline(agent, cfg, sess, ch, dry, once, max_loop):
    """整章流水线：写作 → 润色 → 质检 → 出厂"""
    for program in ("写作", "润色", "质检", "出厂"):
        print(f"\\n{'█' * 74}")
        print(f"█ 第 {ch} 章 · {program}")
        print("█" * 74)
        try:
            run_program(agent, cfg, sess, program, ch, dry, None, once, max_loop)
        except Exception as _e:
            print(f"[错误] {program} 程序失败：{_e}")
            return False
    return True


def _parse_chapters(s):
    """解析章范围：'1-150' / '1,3,5' / '5' → [1,2,...,150] 等"""
    s = (s or "").strip()
    if not s:
        return []
    out = []
    for part in s.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            try:
                a, b = int(a.strip()), int(b.strip())
                out.extend(range(a, b + 1))
            except Exception:
                pass
        else:
            try:
                out.append(int(part))
            except Exception:
                pass
    return out


def _chapter_num(chapter):
    try:
        return int(str(chapter).lstrip("0") or "0")
    except Exception:                              # noqa: BLE001
        return 0
'''
    text = text.replace(OLD, NEW, 1)
    changed.append("run_pipeline + _parse_chapters")

# 8) main 里加 pipeline 分发
OLD = '''    if not args.program:
        print("[提示] 未指定 --program。可用的程序：规划 / 写作 / 润色 / 质检")
        print("       例：python orchestrator.py --program 写作 --chapter 0057 --dry-run")
        cmd_check_session(cfg, sess)
        return

    run_program(agent, cfg, sess, args.program, args.chapter or None,
                args.dry_run, args.phase or None, args.once, args.loop)
    print("\\n编排结束。")'''
if OLD in text and "args.pipeline" not in text:
    NEW = '''    if args.pipeline:
        chs = _parse_chapters(args.chapters)
        if not chs:
            print("[错误] --pipeline 需要 --chapters，例：--chapters 1-150")
            sys.exit(1)
        print(f"\\n流水线模式：共 {len(chs)} 章，程序顺序 写作→润色→质检→出厂")
        for _ch in chs:
            _ch_str = str(_ch).zfill(4)
            print(f"\\n{'=' * 74}")
            print(f"=== 第 {_ch} 章（{_ch_str}）开始 ===")
            print("=" * 74)
            run_pipeline(agent, cfg, sess, _ch_str, args.dry_run, args.once, args.loop)
        print("\\n流水线结束。")
        return

    if not args.program:
        print("[提示] 未指定 --program。可用的程序：规划 / 写作 / 润色 / 质检 / 出厂")
        print("       例：python orchestrator.py --program 写作 --chapter 0057 --dry-run")
        print("       例：python orchestrator.py --pipeline --chapters 1-150")
        cmd_check_session(cfg, sess)
        return

    run_program(agent, cfg, sess, args.program, args.chapter or None,
                args.dry_run, args.phase or None, args.once, args.loop)
    print("\\n编排结束。")'''
    text = text.replace(OLD, NEW, 1)
    changed.append("main pipeline 分发")

# 保存
if changed:
    bak = TARGET.with_suffix(".py.bak_pipeline")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 共 {len(changed)} 处已改：")
    for c in changed:
        print(f"  · {c}")
else:
    print("没有改动")