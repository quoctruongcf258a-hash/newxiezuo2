# fix_review_cap.py — do_review 改成 capture 抓回复 + Python 写 JSON
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''    ok = run_task(agent, task, dry, title=f"盲审 | {app['label']} | {label} | {chunk_label}", app=app)
    if ok and not dry:
        wait_file(out)
    return out
'''

NEW = '''    ok = run_task(agent, task, dry, title=f"盲审 | {app['label']} | {label} | {chunk_label}", app=app)
    if ok and not dry:
        # 用 capture 抓 AI 回复，Python 自己写 JSON（不再依赖 AI 另存）
        try:
            import sys as _s
            _wu = HERE.parent
            if str(_wu) not in _s.path:
                _s.path.insert(0, str(_wu))
            from mix_send import capture_with_meta as _cap
            for _try in range(6):                # 最多等 60 秒
                _r = _cap(app["key"])
                _txt = (_r or {}).get("text", "") if isinstance(_r, dict) else str(_r or "")
                if _txt and _txt.strip():
                    break
                time.sleep(10)
            if _txt and _txt.strip():
                import re as _re
                # 从回复里抠 JSON（第一个 { 到最后一个 }）
                _m = _re.search(r"\\{.*\\}", _txt, _re.S)
                _payload = _m.group(0) if _m else _txt
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(_payload, encoding="utf-8")
                print(f"[盲审] 已抓取并落盘：{out.name}（{len(_payload)} 字）")
            else:
                print(f"[盲审] 未抓到回复：{app['key']}")
        except Exception as _e:
            print(f"[盲审] capture 失败：{_e}")
    return out
'''

if "用 capture 抓 AI 回复" in text:
    print("已改过")
elif OLD not in text:
    print("找不到锚点")
    i = text.find("盲审 | {app['label']}")
    if i >= 0:
        print(repr(text[i:i+400]))
else:
    bak = TARGET.with_suffix(".py.bak_reviewcap")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ do_review 已改用 capture 抓回复")