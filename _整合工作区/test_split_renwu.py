import sys
from pathlib import Path

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator

# ── 1. 调用点上下文（第 760-780 行）──
target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()
print("=== 调用点上下文（第 755-780 行）===")
for j in range(754, 780):
    marker = ">>> " if j == 774 else "    "
    print(f"{marker}{j+1:4d}| {lines[j]}")

# ── 2. 准备测试目录 ──
test_dir = Path(r"F:\赛马23环整合工作室\_整合工作区\_scratch\_test_renwu")
test_dir.mkdir(parents=True, exist_ok=True)
for f in test_dir.glob("*.md"):
    f.unlink()

# ── 3. 假的多人物档案 ──
sample = """# 人物设计：林晚
基础信息：女 / 18 岁 / 青云宗外门弟子 / 出身寒微
外貌：清瘦、眉眼冷冽、左耳有旧伤疤
性格：隐忍 / 倔强 / 护短
表层欲望：进入内门，改变命运
深层欲望：找到当年家族灭门的真相
恐惧：再一次失去在乎的人

# 人物设计：顾行舟
基础信息：男 / 22 岁 / 青云宗内门首席 / 出身名门
外貌：玉树临风、腰间佩剑、眼神冷冽
性格：冷傲 / 正直 / 重情
表层欲望：为家族复仇
深层欲望：找到值得托付一生的人

# 人物设计：苏沐
基础信息：女 / 20 岁 / 药阁弟子 / 药王谷遗孤
外貌：温婉、手上有常年捣药留下的薄茧
性格：温柔 / 聪慧 / 有点小腹黑
表层欲望：炼出能救人的丹药
深层欲望：弥补当年没能救下师父的遗憾
"""

main_path = test_dir / "人物设计.md"
main_path.write_text(sample, encoding="utf-8")
print(f"\n=== 写入测试文件：{main_path.name}（{len(sample)} 字符）===")

# ── 4. 调用拆分 ──
print("\n=== 调用 _split_renwu ===")
orchestrator._split_renwu(main_path, "test_ai")

# ── 5. 列出结果 ──
print(f"\n=== 拆分后目录内容 ===")
files = sorted(test_dir.glob("*.md"))
for f in files:
    print(f"\n  📄 {f.name}  ({f.stat().st_size} B)")
    for ln in f.read_text(encoding="utf-8").splitlines()[:4]:
        print(f"      | {ln}")

print(f"\n共生成 {len(files)} 个文件")
