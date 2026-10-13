import os, shutil, re

R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
SRC = os.path.join(R, "QUEST", "融合")
DST = os.path.join(R, "_融合产物")

# 1. 备份
bak = r"C:\Users\Administrator\Desktop\新书\火影忍者\_七人赛马备份_融合改名前"
if os.path.exists(bak): shutil.rmtree(bak)
shutil.copytree(SRC, bak)
print("备份:", bak)

# 2. 搬运
if os.path.exists(DST): shutil.rmtree(DST)
shutil.copytree(SRC, DST)
print("搬到:", DST)

# 3. 删 README
r = os.path.join(DST, "README.md")
if os.path.exists(r): os.remove(r)

# 4. 去署名
def clean(t):
    t = re.sub(r"QUEST\s*·\s*融合产出文件夹[^\n]*", "融合产物文件夹", t)
    t = re.sub(r"（\s*融合轮\s*·\s*批\d+\s*·\s*QUEST\s*主笔\s*）", "", t)
    t = re.sub(r"融合官[：:]\s*QUEST", "融合官", t)
    t = re.sub(r"融合官\s*[（(]\s*QUEST[^）)]*[)）]", "融合官", t)
    t = re.sub(r"（QUEST[^）)]*融合官[^）)]*）", "", t)
    t = re.sub(r"本席[（(]融合官[)）]", "本席", t)
    t = t.replace("盲审席：QUEST（本局融合官）", "盲审席：QUEST")
    t = t.replace("QUEST（QUEST）", "QUEST")
    t = t.replace("本局融合官", "")
    return t

n = 0
for dp, _, fs in os.walk(DST):
    for fn in fs:
        if not fn.endswith(".md"): continue
        fp = os.path.join(dp, fn)
        t = open(fp, encoding="utf-8").read()
        t2 = clean(t)
        if t2 != t:
            open(fp, "w", encoding="utf-8", newline="\n").write(t2)
            n += 1
print("去署名:", n, "文件")

# 5. 改公共文件
PUB = ["00_总流程说明.md","共享_任务上下文.md","评委_规划轮_评判提示词.md",
       "评委_章纲轮_评判提示词.md","评委_正文轮_评判提示词.md","评委_润色轮_评判提示词.md",
       "评委_盲审与赛马框架.md", os.path.join("自动化","README_自动化流程.md")]

def fixpub(t):
    reps = [
        ("QUEST/融合/", "_融合产物/"),
        ("融合官（QUEST / QUEST）", "融合官"),
        ("融合官（QUEST）", "融合官"),
        ("**QUEST** 做融合", "**融合官**做融合"),
        ("只有 QUEST 做融合", "只有**融合官**做融合"),
        ("只有 QUEST担任融合官", "只有**融合官**担任"),
        ("由 QUEST 产出", "由融合官产出"),
        ("融合由 QUEST专属负责", "融合由融合官专属负责"),
        ("融合由 QUEST专属", "融合由融合官专属"),
        ("QUEST 融合官", "融合官"),
        ("交给 QUEST", "交给融合官"),
        ("发给 QUEST", "发给融合官"),
        ("QUEST 产出", "融合官产出"),
        ("QUEST 融合", "融合官融合"),
        ("QUEST融合", "融合官融合"),
    ]
    for a, b in reps: t = t.replace(a, b)
    return t

for rel in PUB:
    fp = os.path.join(R, rel)
    if not os.path.exists(fp): print("跳过:", rel); continue
    t = open(fp, encoding="utf-8").read()
    t2 = fixpub(t)
    if t2 != t:
        open(fp, "w", encoding="utf-8", newline="\n").write(t2)
        print("改公共:", rel)

# 6. 清 QUEST 侧
for p in [os.path.join(R, "QUEST", "融合"), os.path.join(R, "QUEST", "B_融合任务书.md")]:
    if os.path.exists(p):
        if os.path.isdir(p): shutil.rmtree(p)
        else: os.remove(p)
        print("删:", p)

qfiles = ["QUEST\\00_你的输出位置.md","QUEST\\A1_规划任务书.md","QUEST\\A2_章纲任务书.md",
          "QUEST\\A3_正文任务书.md","QUEST\\A4_润色任务书.md"]
def fixq(t):
    t = t.replace("**QUEST** · **融合官**", "**QUEST**")
    t = t.replace("由你（QUEST）专属负责，但融合只产新文档、不改原文件。", "融合由融合官专属负责。")
    t = t.replace("由你（QUEST）专属负责", "由融合官专属负责")
    t = t.replace("由你本人作为融合官产出", "由融合官产出")
    t = t.replace("（你同时也是融合官，但本轮先作为普通选手产出正文，融合在盲审后由你专属执行。）", "")
    t = t.replace("（你同时是融合官，盲审后由你专属做最终融合。）", "")
    t = t.replace("你同时是融合官，本任务书是你的参赛任务（产出放 `产出/`），与融合工作（放 `融合/`）分开。", "")
    t = t.replace("，由你（QUEST）专属，融合只产新文档不改原文件。", "。")
    t = t.replace("| 融合产出（仅融合官） | `融合\\` |", "")
    return t

for rel in qfiles:
    fp = os.path.join(R, rel)
    if not os.path.exists(fp): continue
    t = open(fp, encoding="utf-8").read()
    t2 = fixq(t)
    if t2 != t:
        open(fp, "w", encoding="utf-8", newline="\n").write(t2)
        print("改Q:", rel)

print("第一步完成")