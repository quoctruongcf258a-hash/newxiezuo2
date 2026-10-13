import os
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
NEED = ["章纲_0_总纲.md","章纲_1_分章章纲.md","章纲_2_人物表现要点.md","章纲_3_衔接设计.md","章纲_4_自评.md"]

print("=" * 70)
print(f"{'选手':12} {'0':>4} {'1':>4} {'2':>4} {'3':>4} {'4':>4} {'总稿':>6}")
print("=" * 70)
missing = []
for p in P:
    d = os.path.join(R, p, "产出", "章纲轮")
    if not os.path.isdir(d):
        print(f"{p:12} 目录不存在"); continue
    files = os.listdir(d)
    marks = []
    for i, need in enumerate(NEED):
        if need in files:
            sz = os.path.getsize(os.path.join(d, need))
            marks.append(f"{sz//1024 or sz:>4}")
        else:
            marks.append("   ✗")
            missing.append((p, need))
    zg = "✅" if any("总稿" in f for f in files) else "✗"
    print(f"{p:12} " + " ".join(marks) + f" {zg:>6}")

print("\n=== 缺的 ===")
for p, n in missing:
    print(f"  {p} 缺 {n}")

# 生成补发指令
if missing:
    print("\n=== 生成补发指令 ===")
    for p, n in missing:
        idx = n.split("_")[1]
        content = f"""【章纲轮 · 补写】

你是「七人赛马」选手 {p}。

你上一轮的章纲缺了一个文件：`{n}`。

请**只补写这一份**，写到：
C:\\Users\\Administrator\\Desktop\\新书\\火影忍者\\七人赛马\\{p}\\产出\\章纲轮\\{n}

内容：本版本亮点与创新点（对照 8 维哪里胜出）。200-500 字。

参考你已写的其他章纲文件（同目录下）保持一致性。

完成后回一句：「补写完成」
"""
        out = os.path.join(R, "资料", "指令", "章纲轮", f"_补_{p}.txt")
        open(out, "w", encoding="utf-8").write(content)
        print(f"  已写: {out}")
