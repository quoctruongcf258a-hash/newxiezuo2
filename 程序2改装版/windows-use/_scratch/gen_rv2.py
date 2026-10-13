import os, io, json
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(R, "资料", "指令", "章纲轮评审")
os.makedirs(CMD, exist_ok=True)

assign = json.load(open(os.path.join(R, "资料", "指令", "章纲轮评审_分配.json"), encoding="utf-8"))

def read_outline(name):
    d = os.path.join(R, name, "产出", "章纲轮")
    if not os.path.isdir(d): return ""
    chunks = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"): continue
        if "总稿" in fn: continue
        with open(os.path.join(d, fn), encoding="utf-8", errors="ignore") as f:
            t = f.read()
        chunks.append(f"\n\n--- {name}/{fn} ---\n{t}\n")
    return "".join(chunks)

TPL = """【章纲轮 · 互审 · 第{b}批】

你是「七人赛马」选手 **{me}**。本批你要评审 **{opp}** 的章纲。

## 评审标准（严格按此）
1. 8 维打分（每维 0-10）：兼容 / 结构 / 衔接 / 角色 / 创意 / 节奏 / 文笔 / 落地
2. 每维写备注（好在哪 / 有什么问题）
3. ≥3 张问题定位卡（致命/严重优先）
4. 1-3 条亮点备注（供融合吸收）
5. 结论：通过 / 打回（踩红线=打回）
6. 切 4 个视角交叉验证：适配人群镜 / 原著时间线镜 / 人物特点镜 / 自洽镜

## 章纲特有检查（新增）
- 16 字段齐全（每章都有 1.目标~16.钩子类型）
- 章节类型判定 + 模板挂载正确（峰值/冲突/解密/日常/过渡）
- 通用 6 要素命中：断章钩/代价/未闭合问题/微兑现/情绪刺激/钩型不重复
- 冲突值：常规章≥8、峰值章≥16
- Strand 比例：主线 55-65% / 情感 20-30% / 世界观 10-20%
- 峰值章：思考+对话节拍<10%

## 输出位置
写到：{root}\\{me}\\评审\\章纲轮\\评审_{opp}.md

## 报告结构
【8维评分卡 · {opp}】
1 兼容：__/10  备注：
2 结构：__/10  备注：
3 衔接：__/10  备注：
4 角色：__/10  备注：
5 创意：__/10  备注：
6 节奏：__/10  备注：
7 文笔：__/10  备注：
8 落地：__/10  备注：
总分：__/80
亮点备注：<1-3条>
致命/严重问题：<无 / 描述>
是否通过：<通过 / 打回>

【问题定位卡】×≥3
- 位置：
- 问题类型：
- 具体描述：
- 严重程度：<致命|严重|一般|轻微>
- 修改建议：

【章纲特有核对】
- 16 字段：<齐全 / 缺X>
- 章节类型：<判定对/错>
- 6 要素：<全/缺X>
- 冲突值：<达标/不达标>
- Strand：<达标/不达标>

## 完成后
回一句：「{me} 第{b}批完成」

════════════════════════════════════════════════
## {opp} 的章纲全文（5 份）

{body}
"""

count = 0
for me, batches in assign.items():
    for b, opps in enumerate(batches, 1):
        if not opps: continue
        opp = opps[0]
        body = read_outline(opp)
        txt = TPL.format(me=me, b=b, opp=opp, root=R, body=body)
        fp = os.path.join(CMD, f"{me}_第{b}批.txt")
        io.open(fp, "w", encoding="utf-8").write(txt)
        kb = os.path.getsize(fp) / 1024
        print(f"{me}_第{b}批.txt  {kb:5.1f} KB  → 审 {opp}")
        count += 1

print(f"\n共 {count} 份，位置: {CMD}")
