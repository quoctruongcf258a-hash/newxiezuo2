import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

if "_do_produce_renwu" in text:
    print("[SKIP] 已经打过补丁（检测到 _do_produce_renwu）")
    raise SystemExit(0)

bak = TARGET.with_suffix(".py.bak_renwu_v1")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")

changed = 0

# ── 补丁 1：do_produce 顶部加人物设计分支 ──
OLD1 = '''def do_produce(agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
               input_text, out_dir, dry, extra_note="", ai_assist=False):
    """① 产出：一名 AI 产出一版。"""
    out = Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"'''

NEW1 = '''def do_produce(agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
               input_text, out_dir, dry, extra_note="", ai_assist=False):
    """① 产出：一名 AI 产出一版。"""
    # ── 人物设计：每个人物单独调 AI，各自落一个文件 ──
    _pkey = phase_cfg.get("key") or phase_cfg.get("name") or ""
    if "人物设计" in _pkey:
        return _do_produce_renwu(
            agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
            input_text, out_dir, dry, extra_note=extra_note, ai_assist=ai_assist
        )
    out = Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"'''

if OLD1 in text:
    text = text.replace(OLD1, NEW1, 1)
    print("[OK] 补丁1：do_produce 顶部加人物设计分支")
    changed += 1
else:
    print("[FAIL] 补丁1 找不到锚点")

# ── 补丁 2：末尾追加 _do_produce_renwu ──
renwu_func = r'''


def _do_produce_renwu(agent, sess, app, program, phase_cfg, chunk_id, chunk_label,
                       input_text, out_dir, dry, extra_note="", ai_assist=False):
    """人物设计：读名单，为每个人物单独调一次 AI，各自落一个文件。"""
    import json as _json

    _od = Path(out_dir)
    _info = None
    for _p in [_od] + list(_od.parents):
        for _c in (_p / "00_初始化" / "项目信息.json", _p / "项目信息.json"):
            if _c.exists():
                _info = _c
                break
        if _info:
            break

    if not _info:
        print("   [人物设计] 未找到 项目信息.json，退回通用产出")
        _out = Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"
        _out.parent.mkdir(parents=True, exist_ok=True)
        return _out

    try:
        _data = _json.loads(_info.read_text(encoding="utf-8"))
    except Exception as _e:
        print(f"   [人物设计] 读 项目信息.json 失败：{_e}")
        return Path(out_dir) / "versions" / f"{chunk_id}__{app['key']}.md"

    _persons = _data.get("人物设计列表") or []
    if not _persons:
        print("   [人物设计] 人物设计列表为空，跳过")
        return []

    print(f"   [人物设计] 名单 {len(_persons)} 人：{_persons}")

    _versions_dir = Path(out_dir) / "versions"
    _versions_dir.mkdir(parents=True, exist_ok=True)

    _tpl = compose_prompt("PROMPT_PRODUCE.md", program)
    _base_note = format_note(program, phase_cfg)
    if extra_note:
        _base_note = (_base_note + "\n\n【上一轮终审反对意见（必须逐条对应处理）】\n" + extra_note).strip()

    _produced = []
    for _name in _persons:
        _safe = _name.replace("/", "_").replace("\\", "_").replace(":", "_").strip()[:40]
        _out = _versions_dir / f"{_safe}__{app['key']}.md"

        _person_input = input_text
        _person_note = (_base_note or "") + "\n\n【本次任务】只为人物「" + _name + "」写一份完整档案，不要写其他人。"
        _label = f"{program} › {phase_cfg.get('key') or phase_cfg.get('name') or ''} › {_name}"

        if ai_assist:
            _task = tasks_mod.build_scaffold_task(app, _tpl, _person_input, str(_out), _label)
        else:
            _task = tasks_mod.build_produce_task(
                app, _tpl, _person_input, str(_out),
                _label, f"{chunk_label} · {_name}", _person_note
            )

        _ok = run_task(agent, _task, dry,
                       title=f"产出 | {app['label']} | 人物设计 | {_name}",
                       app=app)

        if _ok and not dry:
            wait_file(_out, timeout=60)
            if not (_out.exists() and _out.stat().st_size > 0):
                try:
                    import sys as _s
                    _wu = HERE.parent
                    if str(_wu) not in _s.path:
                        _s.path.insert(0, str(_wu))
                    from mix_send import capture_with_meta as _cap
                    _r0 = _cap(app["key"])
                    _baseline = ((_r0 or {}).get("text", "") if isinstance(_r0, dict) else str(_r0 or "")).strip()
                    _txt = ""
                    for _try in range(30):
                        _r = _cap(app["key"])
                        _cur = ((_r or {}).get("text", "") if isinstance(_r, dict) else str(_r or "")).strip()
                        if _cur and len(_cur) >= 50 and _cur != _baseline:
                            _txt = _cur
                            break
                        time.sleep(6)
                    if _txt:
                        _out.write_text(_txt, encoding="utf-8")
                        print(f"   [人物设计|{_name}] capture 落盘：{_out.name}")
                except Exception as _e:
                    print(f"   [人物设计|{_name}] capture 失败：{_e}")

        if dry:
            _produced.append(_out)
            print(f"   [人物设计|{_name}] (dry-run) {_out.name}")
        elif _out.exists() and _out.stat().st_size > 0:
            _produced.append(_out)
            print(f"   [人物设计|{_name}] [OK] {_out.name}")
        else:
            print(f"   [人物设计|{_name}] [FAIL] 无产出")

    return _produced
'''

text = text.rstrip() + "\n" + renwu_func + "\n"
print("[OK] 补丁2：末尾追加 _do_produce_renwu")
changed += 1

# ── 补丁 3：并发分支兼容 list ──
OLD3 = '''                        v = _fut.result()
                        if v and v.exists() and v.stat().st_size > 0:
                            versions.append(v)
                            print(f"  ✔ {_w['label']} 完成：{v.name}")
                        else:
                            print(f"  ✗ {_w['label']} 无产出")'''

NEW3 = '''                        v = _fut.result()
                        if isinstance(v, list):
                            _got = [x for x in v if x and x.exists() and x.stat().st_size > 0]
                            versions.extend(_got)
                            print(f"  ✔ {_w['label']} 完成：{len(_got)} 个人物档案")
                        elif v and v.exists() and v.stat().st_size > 0:
                            versions.append(v)
                            print(f"  ✔ {_w['label']} 完成：{v.name}")
                        else:
                            print(f"  ✗ {_w['label']} 无产出")'''

if OLD3 in text:
    text = text.replace(OLD3, NEW3, 1)
    print("[OK] 补丁3：并发分支兼容 list")
    changed += 1
else:
    print("[FAIL] 补丁3 找不到锚点")

# ── 补丁 4：串行分支兼容 list ──
OLD4 = '''            for w in writers:
                v = do_produce(agent, sess, w, program, phase_cfg, cid, clabel,
                               input_text, out_dir, dry, extra_note=extra_issues,
                               ai_assist=assist)
                if dry or (v.exists() and v.stat().st_size > 0):
                    versions.append(v)'''

NEW4 = '''            for w in writers:
                v = do_produce(agent, sess, w, program, phase_cfg, cid, clabel,
                               input_text, out_dir, dry, extra_note=extra_issues,
                               ai_assist=assist)
                if isinstance(v, list):
                    versions.extend([x for x in v if x])
                elif dry or (v.exists() and v.stat().st_size > 0):
                    versions.append(v)'''

if OLD4 in text:
    text = text.replace(OLD4, NEW4, 1)
    print("[OK] 补丁4：串行分支兼容 list")
    changed += 1
else:
    print("[FAIL] 补丁4 找不到锚点")

# ── 补丁 5：兜底触发条件支持 name ──
OLD5 = '''        # 人物设计环节：拆成 N 个文件（每人一份）
        if phase_cfg.get("key") == "人物设计" and out.exists() and out.stat().st_size > 0:'''

NEW5 = '''        # 人物设计环节：拆成 N 个文件（每人一份）
        _pkey2 = phase_cfg.get("key") or phase_cfg.get("name") or ""
        if "人物设计" in _pkey2 and out.exists() and out.stat().st_size > 0:'''

if OLD5 in text:
    text = text.replace(OLD5, NEW5, 1)
    print("[OK] 补丁5：兜底触发条件支持 name")
    changed += 1
else:
    print("[FAIL] 补丁5 找不到锚点")

if changed >= 4:
    TARGET.write_text(text, encoding="utf-8")
    print(f"\n[OK] 已写回：{TARGET.name}（共 {changed} 处修改）")
else:
    print(f"\n[WARN] 只成功 {changed} 处，未写回（避免半成品）")
