# patch_orch_cdp.py — run_task 优先走 CDP，失败才回退 windows_use
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")


def main():
    print("=" * 60)
    print("patch_orch_cdp")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_CDP_FIRST" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_cdp")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # ── 改动 1：run_task 改成 CDP 优先 ──
    old1 = '''def run_task(agent, task_text, dry=False, title=""):
    print("\\n" + "─" * 74)
    if title:
        print(f"[{title}]")
    print(task_text)
    print("─" * 74)
    if dry:
        print("[dry-run] 未实际驱动。")
        return True
    try:
        agent.invoke(task=task_text)
        return True
    except Exception as e:                     # noqa: BLE001
        print(f"[错误] Windows-Use 执行失败：{e}")
        return False
'''

    new1 = '''def _extract_prompt(task_text):
    """从 SOP 里抠出『指令开始...指令结束』之间的正文。"""
    i = task_text.find("===== 指令开始 =====")
    j = task_text.find("===== 指令结束 =====")
    if i >= 0 and j > i:
        return task_text[i + len("===== 指令开始 ====="):j].strip()
    return task_text


def run_task(agent, task_text, dry=False, title="", app=None):
    """_CDP_FIRST：优先走 CDP（app 有 cdpPort），失败/无端口才回退 windows_use。"""
    print("\\n" + "─" * 74)
    if title:
        print(f"[{title}]")
    print(task_text)
    print("─" * 74)
    if dry:
        print("[dry-run] 未实际驱动。")
        return True

    # ── CDP 分支 ──
    cdp_port = (app or {}).get("cdpPort")
    if cdp_port:
        try:
            import sys as _sys
            _wu = HERE.parent
            if str(_wu) not in _sys.path:
                _sys.path.insert(0, str(_wu))
            from mix_send import send as _cdp_send
            prompt = _extract_prompt(task_text)
            label = (app or {}).get("label") or (app or {}).get("key") or ""
            print(f"[CDP] 发送到 {label}（端口 {cdp_port}），prompt {len(prompt)} 字")
            r = _cdp_send(label, prompt)
            print(f"[CDP] 返回：{r}")
            return True
        except Exception as e:                 # noqa: BLE001
            print(f"[CDP 失败] {e}，回退 windows_use")

    # ── windows_use 分支 ──
    if agent is None:
        print("[错误] agent=None 且该 AI 无 cdpPort，无法执行")
        return False
    try:
        agent.invoke(task=task_text)
        return True
    except Exception as e:                     # noqa: BLE001
        print(f"[错误] Windows-Use 执行失败：{e}")
        return False
'''
    if old1 not in text:
        print("[失败] 找不到 run_task 原函数")
        return
    text = text.replace(old1, new1, 1)
    print("✔ 改动1：run_task 改成 CDP 优先")

    # ── 改动 2：所有 run_task 调用点补 app=xxx ──
    call_patches = [
        ('ok = run_task(agent, task, dry, title=f"产出 | {app[\'label\']} | {label} | {chunk_label}")',
         'ok = run_task(agent, task, dry, title=f"产出 | {app[\'label\']} | {label} | {chunk_label}", app=app)'),
        ('ok = run_task(agent, task, dry, title=f"盲审 | {app[\'label\']} | {label} | {chunk_label}")',
         'ok = run_task(agent, task, dry, title=f"盲审 | {app[\'label\']} | {label} | {chunk_label}", app=app)'),
        ('ok = run_task(agent, task, dry, title=f"拼接 | {app[\'label\']} | {label} | {chunk_label}")',
         'ok = run_task(agent, task, dry, title=f"拼接 | {app[\'label\']} | {label} | {chunk_label}", app=app)'),
        ('ok = run_task(agent, task, dry, title=f"终审投票 | {p[\'label\']} | {gate} 第{rnd}轮")',
         'ok = run_task(agent, task, dry, title=f"终审投票 | {p[\'label\']} | {gate} 第{rnd}轮", app=p)'),
        ('run_task(agent, task, dry, title=f"探测 | {p[\'label\']}")',
         'run_task(agent, task, dry, title=f"探测 | {p[\'label\']}", app=p)'),
    ]
    n = 0
    for a, b in call_patches:
        if a in text:
            text = text.replace(a, b, 1)
            n += 1
    print(f"✔ 改动2：{n}/{len(call_patches)} 个 run_task 调用点补了 app= 参数")

    # ── 改动 3：get_agent 失败不崩 ──
    old3 = '    agent = None if args.dry_run else get_agent()\n'
    new3 = '''    agent = None
    if not args.dry_run:
        try:
            agent = get_agent()
        except Exception as _e:
            print(f"[警告] windows_use agent 初始化失败（{_e}）")
            print("       若所有 AI 都走 CDP，可继续运行；否则需要 Ollama。")
            agent = None
'''
    if old3 in text:
        text = text.replace(old3, new3, 1)
        print("✔ 改动3：get_agent 失败不崩，返回 None")
    else:
        print("[警告] 找不到 agent = None if args.dry_run 锚点")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()