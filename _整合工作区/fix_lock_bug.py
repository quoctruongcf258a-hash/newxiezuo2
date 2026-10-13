# fix_lock_bug.py — 修 _produce_locked / _review_locked 的默认参数 bug
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")
changed = []

# 修 writers
OLD_W = '''                def _produce_locked(_w=w):
                    with _get_ai_lock(_w["key"]):
                        return do_produce(agent, sess, _w, program, phase_cfg,
                                          cid, clabel, input_text, out_dir, dry,
                                          extra_note=extra_issues, ai_assist=assist)
                for w in writers:
                    _futs[_ex.submit(_produce_locked)] = w'''
NEW_W = '''                def _produce_locked(_w):
                    with _get_ai_lock(_w["key"]):
                        return do_produce(agent, sess, _w, program, phase_cfg,
                                          cid, clabel, input_text, out_dir, dry,
                                          extra_note=extra_issues, ai_assist=assist)
                for w in writers:
                    _futs[_ex.submit(_produce_locked, w)] = w'''
if "def _produce_locked(_w):" in text:
    print("writers 已修")
elif OLD_W in text:
    text = text.replace(OLD_W, NEW_W, 1)
    changed.append("writers")
else:
    print("✗ writers 锚点不匹配")

# 修 reviews
OLD_R = '''                def _review_locked(_v=v, _r=r):
                    with _get_ai_lock(_r["key"]):
                        return do_review(agent, sess, _r, program, phase_cfg,
                                         cid, clabel, _v, out_dir, dry, std=_std)
                for v, r in _review_jobs:
                    _futs[_ex.submit(_review_locked)] = (v, r)'''
NEW_R = '''                def _review_locked(_v, _r):
                    with _get_ai_lock(_r["key"]):
                        return do_review(agent, sess, _r, program, phase_cfg,
                                         cid, clabel, _v, out_dir, dry, std=_std)
                for v, r in _review_jobs:
                    _futs[_ex.submit(_review_locked, v, r)] = (v, r)'''
if "def _review_locked(_v, _r):" in text:
    print("reviews 已修")
elif OLD_R in text:
    text = text.replace(OLD_R, NEW_R, 1)
    changed.append("reviews")
else:
    print("✗ reviews 锚点不匹配")

if changed:
    bak = TARGET.with_suffix(".py.bak_lockbug")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    for c in changed:
        print(f"✔ 修了 {c}")
else:
    print("没有改动")