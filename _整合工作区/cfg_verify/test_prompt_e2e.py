# -*- coding: utf-8 -*-
"""端到端验证：环节提示词占位符是否全部替换、task 是否有实质内容。"""
import io, os, re, shutil, sys, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
APP = r"F:\赛马23环整合工作室\程序2改装版\app"
sys.path.insert(0, APP)
import paths, phase_runner as pr, build_project_config as bpc

TMP = r"F:\赛马23环整合工作室\_整合工作区\cfg_verify\prompt_e2e"
shutil.rmtree(TMP, ignore_errors=True)
proj = os.path.join(TMP, "项目P")
os.makedirs(proj, exist_ok=True)
cfg = os.path.join(proj, "config")
bpc.build_config("通用37环", cfg)
paths.set_active_project_cfg(cfg)

captured = []


def fake_ai(role, ai_name, prompt, log_fn=print):
    captured.append((role, ai_name, prompt))
    return "【产出】"


pr.set_call_ai(fake_ai)

# 造上游输入，让 {{输入}} 有东西可填
inp = os.path.join(proj, "00_初始化", "input.md")
os.makedirs(os.path.dirname(inp), exist_ok=True)
open(inp, "w", encoding="utf-8").write("【上游资料】主角林川，题材玄幻，章节数10。")
with open(os.path.join(proj, "00_初始化", "项目信息.json"), "w", encoding="utf-8") as f:
    f.write('{"题材":"玄幻","主角":"林川","章节数":10}')

# 1) 跑 03_去AI 的 R1_润色（验证继承的全局模板 + 占位符替换）
pd = os.path.join(proj, "03_去AI")
os.makedirs(os.path.join(pd, "R1_润色"), exist_ok=True)
open(os.path.join(pd, "R1_润色", "input.md"), "w", encoding="utf-8").write("【待润色正文】原始正文一段。")
pr.run_subphase(pd, "R1_润色", os.path.join(pd, "R1_润色", "input.md"), log_fn=lambda m: None)

# 2) 跑 05_出厂 的 5-1（验证 {{项目信息}}/{{上一环节产出}} 兼容）
pd2 = os.path.join(proj, "05_出厂")
os.makedirs(os.path.join(pd2, "5-1_低级错误"), exist_ok=True)
open(os.path.join(pd2, "5-1_低级错误", "input.md"), "w", encoding="utf-8").write("【上一环节定稿】正文定稿内容。")
pr.run_subphase(pd2, "5-1_低级错误", os.path.join(pd2, "5-1_低级错误", "input.md"),
                log_fn=lambda m: None)

# 3) 复合环分段（W3_正文/显）——验证段落模板 + 段职责注入
pd3 = os.path.join(proj, "02_写作", "第001章")
pr.run_phase("02_写作", log_fn=lambda m: None, project_dir=proj, chapter="第001章")

bad = []
for role, ai, prompt in captured:
    left = re.findall(r"(?<!\{)\{\{?(输入|平台规则|产物目录|项目信息|上一环节产出)\}?\}", prompt)
    if left:
        bad.append((role, ai, left))
    # 赛马写手的任务必须够长（fake AI 只会让旧三角色路径的"调整者"偏短，不算问题）
    if role.startswith("写手") and len(prompt.strip()) < 200:
        bad.append((role, ai, "写手任务过短:%d" % len(prompt)))

print("共捕获 %d 次 AI 调用" % len(captured))
for role, ai, p in captured[:2]:
    print("\n" + "=" * 58)
    print("任务：%s / %s" % (role, ai))
    print("-" * 58)
    print(p[:600])

print("\n" + "=" * 58)
seg = [p for r, a, p in captured if "显段" in p]
if seg:
    print("复合环 显段 模板尾部：")
    print(seg[0][-260:])
    assert "本段专属职责（显段）" in seg[0], "分段模板应注入段职责"

print("\n未替换占位符 / 过短内容：", bad if bad else "无✅")
assert not bad, "仍有未替换占位符"
assert captured, "未捕获到 AI 调用"
print("\n=== ALL PASS ===")
shutil.rmtree(TMP, ignore_errors=True)