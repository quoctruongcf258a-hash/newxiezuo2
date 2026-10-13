# fix_parallel.py — run_mesh_phase 里 writers 和 reviewers 改成并发
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

# 1) 文件头加 import
if "from concurrent.futures import" not in text:
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("import ") or ln.startswith("from "):
            lines.insert(i, "from concurrent.futures import ThreadPoolExecutor, as_completed")
            break
    text = "\n".join(lines)
    print("✔ 加了 ThreadPoolExecutor import")

# 2) 替换 writers 循环
OLD_W = '''    for cid, clabel, _std in chunks:
        writers = phase_writers[:1] if once else phase_writers
        versions = []
        for w in writers:
            v = do_produce(agent, sess, w, program, phase_cfg, cid, clabel,
                           input_text, out_dir, dry, extra_note=extra_issues,
                           ai_assist=assist)
            if dry or (v.exists() and v.stat().st_size > 0):
                versions.append(v)
        if dry and not versions:
            versions = [Path(out_dir) / "versions" / f"{cid}__{w['key']}.md" for w in writers]
'''

NEW_W = '''    for cid, clabel, _std in chunks:
        writers = phase_writers[:1] if once else phase_writers
        versions = []
        # 并发发送：4 个写手同时发任务
        if not dry and len(writers) > 1:
            print(f"\\n[并发] {len(writers)} 个写手同时发送块「{clabel}」...")
            with ThreadPoolExecutor(max_workers=len(writers)) as _ex:
                _futs = {}
                for w in writers:
                    _futs[_ex.submit(
                        do_produce, agent, sess, w, program, phase_cfg,
                        cid, clabel, input_text, out_dir, dry,
                        extra_note=extra_issues, ai_assist=assist
                    )] = w
                for _fut in as_completed(_futs):
                    _w = _futs[_fut]
                    try:
                        v = _fut.result()
                        if v and v.exists() and v.stat().st_size > 0:
                            versions.append(v)
                            print(f"  ✔ {_w['label']} 完成：{v.name}")
                        else:
                            print(f"  ✗ {_w['label']} 无产出")
                    except Exception as _e:
                        print(f"  ✗ {_w['label']} 异常：{_e}")
        else:
            # 单写手或 dry-run：串行
            for w in writers:
                v = do_produce(agent, sess, w, program, phase_cfg, cid, clabel,
                               input_text, out_dir, dry, extra_note=extra_issues,
                               ai_assist=assist)
                if dry or (v.exists() and v.stat().st_size > 0):
                    versions.append(v)
        if dry and not versions:
            versions = [Path(out_dir) / "versions" / f"{cid}__{w['key']}.md" for w in writers]
'''

if "[并发]" in text:
    print("writers 已改过")
elif OLD_W not in text:
    print("✗ 找不到 writers 循环锚点")
    i = text.find("for cid, clabel, _std in chunks:")
    if i >= 0:
        print(repr(text[i:i+600]))
else:
    text = text.replace(OLD_W, NEW_W, 1)
    print("✔ writers 循环已改并发")

# 3) 替换 reviews 循环
OLD_R = '''        reviews = []
        for v in versions:
            writer_key = v.stem.split("__")[-1]
            for r in phase_reviewers:
                if r["key"] == writer_key:
                    continue                       # 不审自己写的
                rv = do_review(agent, sess, r, program, phase_cfg, cid, clabel,
                               v, out_dir, dry, std=_std)
                if rv:
                    reviews.append(rv)
'''

NEW_R = '''        reviews = []
        # 收集所有 (版本, 审核者) 组合
        _review_jobs = []
        for v in versions:
            writer_key = v.stem.split("__")[-1]
            for r in phase_reviewers:
                if r["key"] == writer_key:
                    continue                       # 不审自己写的
                _review_jobs.append((v, r))

        # 并发盲审
        if not dry and len(_review_jobs) > 1:
            print(f"\\n[并发] {len(_review_jobs)} 个盲审同时发送...")
            with ThreadPoolExecutor(max_workers=min(4, len(_review_jobs))) as _ex:
                _futs = {}
                for v, r in _review_jobs:
                    _futs[_ex.submit(
                        do_review, agent, sess, r, program, phase_cfg,
                        cid, clabel, v, out_dir, dry, std=_std
                    )] = (v, r)
                for _fut in as_completed(_futs):
                    v, r = _futs[_fut]
                    try:
                        rv = _fut.result()
                        if rv:
                            reviews.append(rv)
                            print(f"  ✔ {r['label']} 审 {v.stem.split('__')[-1]} 完成")
                        else:
                            print(f"  ✗ {r['label']} 审 {v.stem.split('__')[-1]} 无产出")
                    except Exception as _e:
                        print(f"  ✗ {r['label']} 异常：{_e}")
        else:
            for v, r in _review_jobs:
                rv = do_review(agent, sess, r, program, phase_cfg, cid, clabel,
                               v, out_dir, dry, std=_std)
                if rv:
                    reviews.append(rv)
'''

if "[并发] {len(_review_jobs)}" in text:
    print("reviews 已改过")
elif OLD_R not in text:
    print("✗ 找不到 reviews 循环锚点")
else:
    text = text.replace(OLD_R, NEW_R, 1)
    print("✔ reviews 循环已改并发")

# 保存
bak = TARGET.with_suffix(".py.bak_parallel")
if not bak.exists():
    shutil.copy(TARGET, bak)
    print(f"已备份：{bak.name}")
TARGET.write_text(text, encoding="utf-8")
print("已保存")