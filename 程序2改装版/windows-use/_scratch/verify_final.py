fp = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马\资料\指令\章纲轮终审\公共.txt"
with open(fp, encoding="utf-8") as f:
    t = f.read()

print(f"总字符数: {len(t)}")
print(f"总字节数: {len(t.encode('utf-8'))/1024:.1f} KB")
print()
# 检查版A里的 5 个文件标题
print("=== 版A 应含 5 个文件标题 ===")
for kw in ["章纲_0_总纲", "章纲_1_分章章纲", "章纲_2_人物表现要点", "章纲_3_衔接设计", "章纲_4_自评"]:
    print(f"  {'✅' if kw in t else '❌'} {kw}")
# 检查版B
print("\n=== 版B 特征 ===")
print(f"  {'✅' if '版B 全文' in t else '❌'} 有「版B 全文」标记")
print(f"  {'✅' if '融合_总稿' in t or '融合总稿' in t else '⚠'} 提到融合总稿")

# 显示头尾 200 字
print("\n=== 开头 200 字 ===")
print(t[:200])
print("\n=== 结尾 200 字 ===")
print(t[-200:])
