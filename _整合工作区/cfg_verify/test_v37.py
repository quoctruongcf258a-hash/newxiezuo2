# -*- coding: utf-8 -*-
"""32流程版：模块级AI指派 + 暂停/续跑 + 章节循环 无头验证。"""
import os, sys, json, tempfile, shutil, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
APP = r"F:\赛马23环整合工作室\程序2改装版\app"
sys.path.insert(0, APP)

import paths, phase_runner as pr
from PySide6.QtWidgets import QApplication, QMessageBox
app = QApplication([])

tmp = tempfile.mkdtemp(prefix="v37_")
proj = os.path.join(tmp, "项目A")
os.makedirs(proj, exist_ok=True)

# ---------- 1) 建配置（通用37环模板）----------
import build_project_config as bpc
cfg = os.path.join(proj, "config")
res = bpc.build_config("通用37环", cfg)
paths.set_active_project_cfg(cfg)
print("模板:", res["template"], "| 规划环:", res["规划环数"], "| 子项:", res["规划子项数"])

ph = json.load(open(os.path.join(cfg, "phases.json"), encoding="utf-8"))
mods = []
for st in ("01_规划", "02_写作", "03_去AI", "04_审核", "05_出厂"):
    rings = (ph.get("环节") or {}).get(st)
    if rings:
        mods.append({"stage": st, "count": len(rings),
                     "sample": "、".join((r.get("name") if isinstance(r, dict) else str(r))
                                         for r in rings[:2])})
print("模块:", [(m["stage"], m["count"]) for m in mods])
assert [m["count"] for m in mods if m["stage"] in ("01_规划", "02_写作", "03_去AI", "04_审核")] \
       == [23, 4, 1, 9], "环数应为 23/4/1/9"

# ---------- 2) 模块级指派（绿灯3个AI）----------
import collab_app as ca
alive = {"A1": True, "A2": True, "A3": True, "OFF1": False, "OFF2": False}
ai_names = ["A1", "A2", "A3", "OFF1", "OFF2"]
as_path = os.path.join(cfg, "assignments.json")
assigns = json.load(open(as_path, encoding="utf-8")) or {}

dlg = ca._AssignModuleDialog(mods, assigns, ai_names, alive, as_path)
print("绿灯候选:", dlg.green)
assert dlg.green == ["A1", "A2", "A3"], "候选应只含绿灯AI"
assert set(dlg.rows.keys()) == {m["stage"] for m in mods}

# 选A1/A2/A3 为所有模块写手+裁判；汇总选A1
for st, w in dlg.rows.items():
    for n in ("A1", "A2", "A3"):
        w["writers"][n].setChecked(True)
        w["judges"][n].setChecked(True)
    w["merger"].setCurrentText("A1")
    w["审核"].setCurrentText("A2")
    w["调整"].setCurrentText("A3")
dlg._save()
a2 = json.load(open(as_path, encoding="utf-8"))
node = a2["环节"]["01_规划"]
det0 = next(iter((node.get("明细") or {}).values()), {})
print("01_规划 环节级 writers:", node.get("writers"),
      "| 环明细残留writers:", "writers" in det0,
      "| 环 mode 保留:", det0.get("mode"))
assert node["writers"] == ["A1", "A2", "A3"] and node["merger"] == "A1"
assert "writers" not in det0 and det0.get("mode"), "环明细应只清AI键、保留mode"

# ---------- 3) 校验拦截：写手只选1 ----------
warns = []
QMessageBox.warning = staticmethod(lambda *a, **k: warns.append(a[2]))
dlg2 = ca._AssignModuleDialog(mods, a2, ai_names, alive, as_path)
w = dlg2.rows["02_写作"]
for n in ("A1", "A2", "A3"):
    w["writers"][n].setChecked(False)
w["writers"]["A1"].setChecked(True)   # 只1个 → 应拦截
dlg2._save()
print("拦截提示数:", len(warns), "|", (warns[0][:52] if warns else "无"))
assert len(warns) >= 1, "写手<2 应拦截"

# ---------- 4) 引擎：伪AI ----------
calls = []
def fake_ai(role, ai_name, prompt, log_fn=print):
    calls.append((role, ai_name))
    return f"【{ai_name}·{role}】产出"
pr.set_call_ai(fake_ai)

# 4a) 暂停+续跑：01_规划 跑2环后暂停
orig = pr.run_subphase
def counting(phase_dir, sub_name, input_file, log_fn=print, item_desc="", stage_key=None):
    out = orig(phase_dir, sub_name, input_file, log_fn=log_fn, item_desc=item_desc,
               stage_key=stage_key)
    if out and "__" not in sub_name:          # 普通环（子项环用 __ 分隔，不计）
        if len(pr._TEST_DONE) >= 2:
            pr.request_pause()
        else:
            pr._TEST_DONE.append(sub_name)
    return out
pr._TEST_DONE = []
pr.run_subphase = counting

r = pr.run_phase("01_规划", log_fn=lambda m: None, project_dir=proj)
print("首次运行返回:", r, "| 已完成环:", len(pr._TEST_DONE))
assert r == "PAUSED" and len(pr._TEST_DONE) == 2, "应跑2环后暂停"
assert os.path.exists(os.path.join(proj, "01_规划", "暂停.json"))

# 4b) 换指派（模拟用户改AI）+ 续跑 → 跳过已完成，只补剩下
a3 = json.load(open(as_path, encoding="utf-8"))
a3["环节"]["01_规划"]["writers"] = ["A2", "A3"]
a3["环节"]["01_规划"]["judges"] = ["A1", "A3"]
json.dump(a3, open(as_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
done_before = set(pr._TEST_DONE)
n_calls_before = len(calls)
pr.clear_pause()
pr.run_subphase = orig
pr._TEST_DONE = []
import glob
pr.request_pause = pr.request_pause

# 用第三轮计数：跑满全部剩余
r2 = pr.run_phase("01_规划", log_fn=lambda m: None, project_dir=proj, resume=True)
fin = glob.glob(os.path.join(proj, "01_规划", "*", "final.md"))
# human 环（AI出候选→停住等人工拍板）不产出 final，产出 candidate.md + pending.json
adet = json.load(open(as_path, encoding="utf-8"))["环节"]["01_规划"]["明细"]
human = [k for k, v in adet.items() if (v.get("mode") == "human")]
lock = [k for k, v in adet.items() if (v.get("mode") == "lock")]
cand = glob.glob(os.path.join(proj, "01_规划", "*", "candidate.md"))
aud = glob.glob(os.path.join(proj, "01_规划", "*", "audit.md"))
wait = human + lock
print("续跑返回:", os.path.basename(str(r2)), "| final:", len(fin),
      "| human环:", len(human), "| lock环:", len(lock), "| candidate:", len(cand))
assert len(fin) == 23 - len(wait), f"非human/lock环应都有final；期望{23-len(wait)} 实际{len(fin)}"
assert len(cand) == len(human) and len(aud) == len(lock), "human出candidate / lock出audit"

# ---------- 5) 章节循环 run_book（2章）----------
bdir = os.path.join(proj, "02_写作")
r3 = pr.run_book(proj, chapters=2, log_fn=lambda m: None, resume=True)
ch_dirs = sorted([d for d in os.listdir(bdir) if d.startswith("第")]) if os.path.isdir(bdir) else []
print("章节目录:", ch_dirs)
assert "第001章" in ch_dirs and "第002章" in ch_dirs, "应生成两章目录"
for ch in ("第001章", "第002章"):
    assert os.path.isdir(os.path.join(proj, "03_去AI", ch)), f"润色缺 {ch}"
    assert os.path.isdir(os.path.join(proj, "04_审核", ch)), f"审核缺 {ch}"
body1 = os.path.join(proj, "02_写作", "第001章", "W3_正文", "第001章_正文.md")
print("第001章正文拼接文件:", os.path.exists(body1))
assert os.path.exists(body1), "W3 复合环应拼出正文"

# ---------- 6) 进度扫描 ----------
def ring_paths(pdir, r, chapter=None):
    return pr._ring_final_paths(pdir, r, chapter)
total_ok = total = 0
det_all = json.load(open(as_path, encoding="utf-8"))["环节"]
for st in ("01_规划", "02_写作", "03_去AI", "04_审核"):
    rings = ph["环节"][st]
    base = os.path.join(proj, st)
    chs = sorted([d for d in os.listdir(base) if d.startswith("第")]) \
        if os.path.isdir(base) else []
    cur = chs[-1] if chs else None
    pdir = os.path.join(base, cur) if cur else base
    ok = 0
    detail = det_all.get(st, {}).get("明细", {})
    for r in rings:
        kind, exp = ring_paths(pdir, r, cur)
        hit = all(os.path.exists(p) for p in exp)
        ok += 1 if hit else 0
        if not hit and cur == "第002章":
            nm = r.get("name") if isinstance(r, dict) else r
            print("     [未产出] %-16s mode=%-6s kind=%s" %
                  (nm, detail.get(nm, {}).get("mode"), kind))
    total_ok += ok; total += len(rings)
    print("  %s: %d/%d" % (st, ok, len(rings)))
print("总进度: %d/%d" % (total_ok, total))

print("\n=== ALL PASS ===")
shutil.rmtree(tmp, ignore_errors=True)