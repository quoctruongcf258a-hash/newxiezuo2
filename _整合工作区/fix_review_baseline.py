# fix_review_baseline.py — do_review 发送前抓 baseline，发送后等新回复
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")
changed = 0

# 替换 do_review 里 capture 段
OLD = '''    ok = run_task(agent, task, dry, title=f"盲审 | {app['label']} | {label} | {chunk_label}", app=app)
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

NEW = '''    # 发送前先抓「当前最后回复」作为 baseline（防止误读旧回复）
    _baseline = ""
    if not dry:
        try:
            import sys as _s
            _wu = HERE.parent
            if str(_wu) not in _s.path:
                _s.path.insert(0, str(_wu))
            from mix_send import capture_with_meta as _cap0
            _r0 = _cap0(app["key"])
            _baseline = ((_r0 or {}).get("text", "") if isinstance(_r0, dict) else str(_r0 or "")).strip()
        except Exception:
            _baseline = ""

    ok = run_task(agent, task, dry, title=f"盲审 | {app['label']} | {label} | {chunk_label}", app=app)
    if ok and not dry:
        # 用 capture 抓 AI 回复，Python 自己写 JSON（不再依赖 AI 另存）
        try:
            import sys as _s
            _wu = HERE.parent
            if str(_wu) not in _s.path:
                _s.path.insert(0, str(_wu))
            from mix_send import capture_with_meta as _cap
            _txt = ""
            for _try in range(30):                # 最多等 150 秒
                _r = _cap(app["key"])
                _cur = ((_r or {}).get("text", "") if isinstance(_r, dict) else str(_r or "")).strip()
                # 判定：必须有内容 + 内容 ≥ 30 字 + 与 baseline 不同
                if _cur and len(_cur) >= 30 and _cur != _baseline:
                    _txt = _cur
                    break
                time.sleep(5)
            if _txt:
                import re as _re
                # 从回复里抠 JSON（第一个 { 到最后一个 }）
                _m = _re.search(r"\\{.*\\}", _txt, _re.S)
                _payload = _m.group(0) if _m else _txt
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(_payload, encoding="utf-8")
                print(f"[盲审] 已抓取并落盘：{out.name}（{len(_payload)} 字，baseline {len(_baseline)} 字）")
            else:
                print(f"[盲审] 未抓到新回复：{app['key']}（baseline {len(_baseline)} 字）")
        except Exception as _e:
            print(f"[盲审] capture 失败：{_e}")
    return out
'''

if "baseline {len(_baseline)} 字" in text:
    print("已改过")
elif OLD not in text:
    print("✗ 找不到 do_review capture 段")
    i = text.find("用 capture 抓 AI 回复")
    if i >= 0:
        print(repr(text[i-200:i+600]))
else:
    text = text.replace(OLD, NEW, 1)
    changed += 1
    print("✔ do_review 加了 baseline 检查")

# 同样修 do_produce
OLD_P = '''        if not (out.exists() and out.stat().st_size > 0):
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
'''

NEW_P = '''        if not (out.exists() and out.stat().st_size > 0):
            try:
                import sys as _s
                _wu = HERE.parent
                if str(_wu) not in _s.path:
                    _s.path.insert(0, str(_wu))
                from mix_send import capture_with_meta as _cap
                # 先抓 baseline
                _r0 = _cap(app["key"])
                _baseline = ((_r0 or {}).get("text", "") if isinstance(_r0, dict) else str(_r0 or "")).strip()
                _txt = ""
                for _try in range(30):        # 180 秒
                    _r = _cap(app["key"])
                    _cur = ((_r or {}).get("text", "") if isinstance(_r, dict) else str(_r or "")).strip()
                    if _cur and len(_cur) >= 50 and _cur != _baseline:
                        _txt = _cur
                        break
                    time.sleep(6)
                if _txt:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(_txt, encoding="utf-8")
                    print(f"[产出] capture 已落盘：{out.name}（{len(_txt)} 字）")
                else:
                    print(f"[产出] capture 未抓到新回复：{app['key']}")
            except Exception as _e:
                print(f"[产出] capture 失败：{_e}")
'''

if "baseline {len(_baseline)} 字" in text and "[产出] capture 已落盘" in text:
    pass  # 已改过
if OLD_P in text:
    text = text.replace(OLD_P, NEW_P, 1)
    changed += 1
    print("✔ do_produce 也加了 baseline 检查")

if changed:
    bak = TARGET.with_suffix(".py.bak_baseline")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    print(f"✔ 共改 {changed} 处")
else:
    print("没有改动")