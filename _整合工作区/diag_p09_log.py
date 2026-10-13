from pathlib import Path

log = Path(r"F:\赛马23环整合工作室\_整合工作区\p09_log.txt")
if log.exists():
    text = log.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    print(f"共 {len(lines)} 行")
    print()
    # 找关键行
    for i, ln in enumerate(lines, 1):
        if any(k in ln for k in [
            "[判定]", "[赛马]", "[串行]", "第 1/3 次", "第 2/3 次", "第 3/3 次",
            "任务已发送", "📊 进度", "✓ 成功", "❌", "⛔", "校验失败", "idle_no_output",
            "AI 连续", "CDP 已发送", "send 返回异常"
        ]):
            print(f"  {i:5d}| {ln.strip()[:130]}")
else:
    print(f"❌ 找不到 {log}")
