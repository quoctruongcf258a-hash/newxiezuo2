import os, io
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
CMD = os.path.join(R, "资料", "指令", "融合轮")

# 读原批3 + 8维表
b3 = open(os.path.join(CMD, "融合_ZCode_批3.txt"), encoding="utf-8").read()
tbl = open(os.path.join(R, "_融合产物", "8维取优来源表.md"), encoding="utf-8").read()

# 在"## 融合方法"前插入 8维表
new = b3.replace("## 融合方法", f"## 8 维取优来源表（写批3时按这个取）\n\n{tbl}\n\n## 融合方法", 1)

with io.open(os.path.join(CMD, "融合_ZCode_批3.txt"), "w", encoding="utf-8") as f:
    f.write(new)
print(f"✅ 批3 已合并 8 维表，新大小: {os.path.getsize(os.path.join(CMD,'融合_ZCode_批3.txt'))/1024:.1f} KB")