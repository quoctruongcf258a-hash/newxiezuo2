import sys, time
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")

from mix_send import send, check_running, is_ai_busy, capture_with_meta, _lookup

print("=" * 70)
print("CodeBuddy 最小测试")
print("=" * 70)

# 1. 配置检查
info = _lookup("CodeBuddy")
print(f"\n[1] _lookup('CodeBuddy') = {info}")

if not info:
    print("❌ 找不到配置，尝试小写 codebuddy")
    info = _lookup("codebuddy")
    print(f"    _lookup('codebuddy') = {info}")

# 2. 忙闲状态
print(f"\n[2] 当前状态：")
try:
    busy = is_ai_busy("CodeBuddy")
    print(f"    is_ai_busy('CodeBuddy') = {busy}")
except Exception as e:
    print(f"    ❌ is_ai_busy 失败：{e}")

# 3. 抓 baseline
print(f"\n[3] 抓 baseline（当前窗口文本）：")
try:
    r0 = capture_with_meta("CodeBuddy")
    base = (r0 or {}).get("text", "") if isinstance(r0, dict) else str(r0 or "")
    print(f"    baseline 长度：{len(base)}")
    print(f"    前 200 字：{base[:200]!r}")
except Exception as e:
    print(f"    ❌ 失败：{e}")

# 4. 发送测试消息
print(f"\n[4] 发送测试消息...")
test_msg = "[系统测试] 请直接回复「测试成功」四个字，不要做其他事情。"
try:
    r = send("CodeBuddy", test_msg)
    print(f"    send 返回：{r}")
except Exception as e:
    print(f"    ❌ send 失败：{e}")
    raise SystemExit()

# 5. 等 5s 看状态
print(f"\n[5] 等 5s 后检查状态...")
time.sleep(5)
try:
    busy = is_ai_busy("CodeBuddy")
    print(f"    is_ai_busy = {busy}")
except Exception as e:
    print(f"    ❌ {e}")

# 6. 抓新文本
print(f"\n[6] 抓发送后文本：")
try:
    r1 = capture_with_meta("CodeBuddy")
    cur = (r1 or {}).get("text", "") if isinstance(r1, dict) else str(r1 or "")
    print(f"    当前长度：{len(cur)}")
    print(f"    与 baseline 不同：{'是' if cur != base else '否'}")
    print(f"    前 300 字：{cur[:300]!r}")
except Exception as e:
    print(f"    ❌ {e}")

print()
print("=" * 70)
print("测试完成")
print("=" * 70)
print("请检查 CodeBuddy 窗口：")
print("  1. 消息是否出现在对话框里？")
print("  2. AI 有没有开始回复「测试成功」？")
