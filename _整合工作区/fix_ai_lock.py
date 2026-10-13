# fix_ai_lock.py — 每个 AI 一把锁，防止同一 AI 被并发调用
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")
changed = []

# 1) 加 import threading + 全局锁字典
if "_AI_LOCKS" not in text:
    # 在 ThreadPoolExecutor import 后插入
    anchor = "from concurrent.futures import ThreadPoolExecutor, as_completed"
    if anchor in text:
        text = text.replace(
            anchor,
            anchor + "\nimport threading\n\n# 每个 AI 一把锁：同一 AI 不能并发调用（CDP 单连接）\n_AI_LOCKS = {}\n_AI_LOCKS_MU = threading.Lock()\n\n\ndef _get_ai_lock(key):\n    with _AI_LOCKS_MU:\n        if key not in _AI_LOCKS:\n            _AI_LOCKS[key] = threading.Lock()\n        return _AI_LOCKS[key]",
            1,
        )
        changed.append("import threading + _AI_LOCKS")
    else:
        print("✗ 找不到 ThreadPoolExecutor import")

# 2) 包装 do_produce 的并发提交，加锁
OLD_W = '''                for w in writers:
                    _futs[_ex.submit(
                        do_produce, agent, sess, w, program, phase_cfg,
                        cid, clabel, input_text, out_dir, dry,
                        extra_note=extra_issues, ai_assist=assist
                    )] = w'''
NEW_W = '''                def _produce_locked(_w=w):
                    with _get_ai_lock(_w["key"]):
                        return do_produce(agent, sess, _w, program, phase_cfg,
                                          cid, clabel, input_text, out_dir, dry,
                                          extra_note=extra_issues, ai_assist=assist)
                for w in writers:
                    _futs[_ex.submit(_produce_locked)] = w'''
if "_produce_locked" in text:
    print("writers 已加锁")
elif OLD_W in text:
    text = text.replace(OLD_W, NEW_W, 1)
    changed.append("writers 加锁")
else:
    print("✗ 找不到 writers 并发块")

# 3) 包装 do_review 的并发提交，加锁
OLD_R = '''                for v, r in _review_jobs:
                    _futs[_ex.submit(
                        do_review, agent, sess, r, program, phase_cfg,
                        cid, clabel, v, out_dir, dry, std=_std
                    )] = (v, r)'''
NEW_R = '''                def _review_locked(_v=v, _r=r):
                    with _get_ai_lock(_r["key"]):
                        return do_review(agent, sess, _r, program, phase_cfg,
                                         cid, clabel, _v, out_dir, dry, std=_std)
                for v, r in _review_jobs:
                    _futs[_ex.submit(_review_locked)] = (v, r)'''
if "_review_locked" in text:
    print("reviews 已加锁")
elif OLD_R in text:
    text = text.replace(OLD_R, NEW_R, 1)
    changed.append("reviews 加锁")
else:
    print("✗ 找不到 reviews 并发块")

# 保存
if changed:
    bak = TARGET.with_suffix(".py.bak_ailock")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    TARGET.write_text(text, encoding="utf-8")
    for c in changed:
        print(f"✔ {c}")
else:
    print("没有改动")