# -*- coding: utf-8 -*-
"""
试运行：验证 37 环机制已真正嵌入执行链路。

用伪 AI（不碰任何真实窗口）跑代表性环，检查：
  · mesh 环是否真的走「N写手 → 匿名盲审 → 汇总择优」
  · human 环是否出候选并停住等人拍板
  · lock 环是否出审计并等人锁
  · 模板是否还会导致整环跳过
"""
import os
import sys
import json
import shutil
import tempfile

BASE = r"F:\赛马23环整合工作室\程序2改装版"
sys.path.insert(0, os.path.join(BASE, "app"))
import paths  # noqa
import phase_runner as pr  # noqa

CALLS = []


def fake_ai(role, ai_name, prompt, log_fn=print):
    CALLS.append((role, ai_name))
    if role.startswith("写手"):
        return f"【{ai_name} 的候选稿】\n这是 {role} 针对任务写的内容。\n任务摘要：{prompt[:60]}"
    if role.startswith("裁判"):
        return "评审：稿件1 结构完整；稿件2 节奏更好；【最佳稿编号】2【最差稿编号】5"
    if role == "汇总者":
        return "【融合最终版】\n综合各稿之长后的定稿内容。"
    if role == "候选生成者":
        return f"【{ai_name} 候选稿】\n待人工拍板。"
    if role == "审计者":
        return "逐项审计：全部通过。总体结论：PASS"
    if role == "审核者":
        return "评审意见：PASS。内容合格。"
    return f"【{ai_name} 产出】"


pr.set_call_ai(fake_ai)


def run_one(stage, ring):
    tmp = tempfile.mkdtemp(prefix="embed_")
    d = os.path.join(tmp, stage)
    os.makedirs(d, exist_ok=True)
    inp = os.path.join(d, "input.md")
    with open(inp, "w", encoding="utf-8") as f:
        f.write("# 上游输入\n（试运行占位）\n")
    print(f"\n{'='*66}")
    print(f"▶ 试运行  {stage} / {ring}")
    print("=" * 66)
    CALLS.clear()
    out = pr.run_subphase(d, ring, inp, log_fn=print)
    ring_dir = os.path.join(d, ring)
    files = sorted(os.listdir(ring_dir)) if os.path.isdir(ring_dir) else []
    print(f"\n  → 返回 final: {os.path.basename(out) if out else 'None（等待人工）'}")
    print(f"  → 产物文件: {files}")
    print(f"  → AI 调用: {len(CALLS)} 次  {CALLS[:8]}{' ...' if len(CALLS) > 8 else ''}")
    shutil.rmtree(tmp, ignore_errors=True)
    return out, files, len(CALLS)


if __name__ == "__main__":
    results = []
    # 代表性环：mesh / human / lock 各一，外加写作核心环
    for stage, ring in [
        ("01_规划", "P04_一句话故事"),
        ("02_写作", "W3_正文"),
        ("03_去AI", "R1_润色"),
        ("04_审核", "Q6_成书检验"),
    ]:
        try:
            results.append((stage, ring) + run_one(stage, ring))
        except Exception as e:
            import traceback
            print(f"  ❌ 异常: {e}")
            traceback.print_exc()

    print(f"\n{'='*66}")
    print("试运行汇总")
    print("=" * 66)
    for stage, ring, out, files, n in results:
        tag = "✅产出 final" if out else "⏸等待人工"
        print(f"  {stage}/{ring:<16} {tag}  产物{len(files)}个  AI调用{n}次")

    # 模板缺失复查
    print("\n=== 全量模板复查（应无缺失）===")
    pp = json.load(open(os.path.join(BASE, "rules", "phases.json"), encoding="utf-8"))
    miss = []
    for st, subs in pp["环节"].items():
        gen = os.path.exists(os.path.join(BASE, "prompts", st, "_通用.md"))
        for s in subs:
            name = s if isinstance(s, str) else s.get("name")
            t = os.path.join(BASE, "prompts", st, name + ".md")
            if not os.path.exists(t) and not gen:
                miss.append(f"{st}/{name}")
    print(f"  仍缺模板或无兜底的环 = {len(miss)}")
    if miss:
        print("   ", miss[:10])
