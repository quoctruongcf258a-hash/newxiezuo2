# verify_step0.py — 验证步骤0的改动
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")

print("=" * 60)
print("1) 故事梗概.md")
print("=" * 60)
p1 = BASE / "prompts" / "00_初始化" / "故事梗概.md"
if p1.exists():
    t = p1.read_text(encoding="utf-8")
    print(f"  字节数: {len(t)}")
    for k in ["冲突处理原则", "金手指处理原则", "方向", "400 字", "不能一次性全给", "分层释放"]:
        ok = "OK" if k in t else "NO"
        print(f"  [{ok}] {k}")
else:
    print("  文件不存在")

print()
print("=" * 60)
print("2) 用户输入.md")
print("=" * 60)
p2 = BASE / "prompts" / "00_初始化" / "用户输入.md"
if p2.exists():
    t = p2.read_text(encoding="utf-8")
    print(f"  字节数: {len(t)}")
    print(f"  前 200 字: {t[:200]!r}")
else:
    print("  文件不存在")

print()
print("=" * 60)
print("3) 旧 no0tisc.md 是否已删")
print("=" * 60)
for path in [
    BASE / "prompts" / "步骤0" / "no0tisc.md",
    BASE / "AI指派协作" / "prompts" / "步骤0" / "no0tisc.md",
]:
    print(f"  {path.relative_to(BASE)}  存在={path.exists()}")