# patch_input_desc.py — 
#   1) phase_input 里注入本环节的任务说明（desc）
#   2) 再次确认删掉 platform_block 里的 AI 政策
#   3) format_note 里的输出格式改名，不再叫「补强要求」
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
TASKS = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")


def patch_orch():
    text = TARGET.read_text(encoding="utf-8")
    changed = 0

    # ── 1. 删 platform_block 里的 AI 政策（如果还有） ──
    ai_line = "    if p.get(\"reviewRedlines\", {}).get(\"aiPolicy\", {}).get(\"平台立场\"):\n"
    if ai_line in text:
        # 找到这 2 行一起删
        i = text.find(ai_line)
        j = text.find("\n", text.find("parts.append", i)) + 1
        text = text[:i] + "    # _NO_AI_POLICY：AI 政策行已删除\n" + text[j:]
        print("✔ platform_block：删掉 AI 政策")
        changed += 1
    else:
        print("· platform_block：AI 政策已无")

    # ── 2. phase_input 注入 desc ──
    anchor = "def phase_input(cfg, program, phase_cfg, chapter) -> str:\n"
    marker = '    parts = []\n    pb = platform_block(cfg)\n'
    if marker not in text:
        print("[失败] 找不到 phase_input 开头的 parts = []")
        return changed

    inject = '''    parts = []

    # _INJECT_DESC：注入本环节的任务说明（来自 rings_items.json 的 desc）
    _desc = (phase_cfg.get("desc") or "").strip()
    _name = phase_cfg.get("key") or phase_cfg.get("name") or ""
    if _desc:
        _task_block = f"【本环节任务说明：{_name}】\\n{_desc}"
        # 从 apps.json 的 auditDirections 找本环归属方向，附上验收标准
        try:
            _dirs = cfg.get("auditDirections") or []
            for _d in _dirs:
                _rings = list(_d.get("rings") or []) + list(_d.get("extends") or [])
                if _name in _rings:
                    _std = _d.get("standards") or []
                    _fail = _d.get("failPatterns") or []
                    if _std:
                        _task_block += "\\n\\n【本方向审核标准（逐条满足）】"
                        for _s in _std:
                            _task_block += f"\\n  □ {_s}"
                    if _fail:
                        _task_block += "\\n\\n【反模式（命中即判不合格）】"
                        for _f in _fail:
                            _task_block += f"\\n  ✗ {_f}"
                    break
        except Exception:
            pass
        parts.append(_task_block)

    pb = platform_block(cfg)
'''
    text = text.replace(marker, inject, 1)
    print("✔ phase_input：注入本环节 desc + 方向标准")
    changed += 1

    TARGET.write_text(text, encoding="utf-8")
    print(f"✔ 已写回 {TARGET}")
    return changed


def patch_tasks():
    """改 tasks.py：把 '本次补强要求' 改名，避免把输出格式当补强"""
    if not TASKS.exists():
        print(f"· {TASKS.name} 不存在，跳过")
        return 0
    text = TASKS.read_text(encoding="utf-8")
    if "_RENAMED_LABELS" in text:
        print("· tasks.py：已改过")
        return 0

    bak = TASKS.with_suffix(".py.bak_labels")
    if not bak.exists():
        shutil.copy(TASKS, bak)
        print(f"已备份：{bak.name}")

    text = text.replace(
        '("本环节输入材料", input_text), ("本次补强要求", extra_note)',
        '("本环节输入材料", input_text), ("输出格式要求", extra_note)  # _RENAMED_LABELS'
    )
    TASKS.write_text(text, encoding="utf-8")
    print("✔ tasks.py：'本次补强要求' 改名为 '输出格式要求'")
    return 1


def main():
    print("=" * 60)
    print("patch_input_desc")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    bak = TARGET.with_suffix(".py.bak_inputdesc")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}\n")

    patch_orch()
    print()
    patch_tasks()

    print("\n完成。下一步：")
    print("  cd ..\\..\\windows-use\\_scratch")
    print("  ..\\.venv\\Scripts\\python.exe orchestrator.py --program 规划 --phase 一句话故事 --dry-run")
    print("  看『本环节任务说明』是否出现")


if __name__ == "__main__":
    main()