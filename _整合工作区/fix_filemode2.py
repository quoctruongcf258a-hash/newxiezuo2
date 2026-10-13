# fix_filemode2.py — 1) _open_instruction 识别 electron  2) do_produce 用 capture 抓回复
import shutil
from pathlib import Path

TASKS = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\tasks.py")
ORCH = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
changed = []

# ─── 1) _open_instruction 加 electron 分支 ───
text = TASKS.read_text(encoding="utf-8")
if "app.get(\"类型\") == \"electron\"" not in text and "'类型') == 'electron'" not in text:
    # 找 _open_instruction 定义
    start = text.find("def _open_instruction")
    if start < 0:
        print("找不到 _open_instruction")
    else:
        end = text.find("\ndef ", start + 5)
        block = text[start:end]
        print("--- _open_instruction 原代码 ---")
        print(block[:800])
        print("---")
        # 在 return 之前插入 electron 检查
        # 简单做法：在函数体开头插入
        insert_at = block.find("):") + 2
        # 找到函数签名结束的位置（第一个换行后）
        sig_end = block.find("\n", insert_at)
        electron_check = '''
    _t = (app or {}).get("类型", "")
    if _t == "electron":
        _exe = (app or {}).get("exe", "") or (app or {}).get("executable", "")
        return (f"启动或聚焦「{app.get('label')}」桌面程序" + (f"（可执行文件：{_exe}）" if _exe else "") + "。若已在运行，直接切换到它的主窗口并置前；若未安装或启动失败，停下并报告「{app.get('label')} 不可用」，不要尝试其它程序。")
'''
        new_block = block[:sig_end] + electron_check + block[sig_end:]
        text = text[:start] + new_block + text[end:]
        TASKS.write_text(text, encoding="utf-8")
        changed.append("_open_instruction electron 分支")
else:
    print("_open_instruction 已改过")

# ─── 2) do_produce 用 capture 抓回复 ───
otext = ORCH.read_text(encoding="utf-8")
OLD_DP = '''    ok = run_task(agent, task, dry, title=f"产出 | {app['label']} | {label} | {chunk_label}", app=app)
    if ok and not dry:
        wait_file(out)
        # 人物设计环节：拆成 N 个文件（每人一份）
        if phase_cfg.get("key") == "人物设计":
            try:
                _split_renwu(out, app["key"])
            except Exception as _e:
                print(f"   [拆分失败] {_e}")
    return out
'''
NEW_DP = '''    ok = run_task(agent, task, dry, title=f"产出 | {app['label']} | {label} | {chunk_label}", app=app)
    if ok and not dry:
        # 先尝试等 AI 自己另存（60 秒）
        wait_file(out, timeout=60)
        # 若没落盘，用 capture 抓回复写文件
        if not (out.exists() and out.stat().st_size > 0):
            try:
                import sys as _s
                _wu = HERE.parent
                if str(_wu) not in _s.path:
                    _s.path.insert(0, str(_wu))
                from mix_send import capture_with_meta as _cap
                _txt = ""
                for _try in range(6):
                    _r = _cap(app["key"])
                    _txt = (_r or {}).get("text", "") if isinstance(_r, dict) else str(_r or "")
                    if _txt and _txt.strip():
                        break
                    time.sleep(10)
                if _txt and _txt.strip():
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(_txt, encoding="utf-8")
                    print(f"[产出] capture 已落盘：{out.name}（{len(_txt)} 字）")
                else:
                    print(f"[产出] capture 未抓到回复：{app['key']}")
            except Exception as _e:
                print(f"[产出] capture 失败：{_e}")
        # 人物设计环节：拆成 N 个文件（每人一份）
        if phase_cfg.get("key") == "人物设计" and out.exists() and out.stat().st_size > 0:
            try:
                _split_renwu(out, app["key"])
            except Exception as _e:
                print(f"   [拆分失败] {_e}")
    return out
'''
if OLD_DP in otext:
    otext = otext.replace(OLD_DP, NEW_DP, 1)
    ORCH.write_text(otext, encoding="utf-8")
    changed.append("do_produce capture 兜底")
elif "[产出] capture 已落盘" in otext:
    print("do_produce 已改过")
else:
    print("找不到 do_produce 锚点")

# 备份
for f, suf in [(TASKS, ".py.bak_fmode2"), (ORCH, ".py.bak_fmode2")]:
    bak = f.with_suffix(suf)
    if not bak.exists():
        shutil.copy(f, bak)
        print(f"已备份：{bak.name}")

for c in changed:
    print(f"✔ {c}")