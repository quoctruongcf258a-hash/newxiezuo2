from pathlib import Path

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = target.read_text(encoding="utf-8")
lines = text.splitlines()

# 找函数定义
i_func = None
for i, ln in enumerate(lines):
    if ln.startswith("def keywords_for_phase"):
        i_func = i
        break

if i_func is None:
    print("❌ 找不到 def keywords_for_phase")
else:
    # 打印到下一个 def 或 80 行
    end = i_func + 1
    while end < len(lines) and end < i_func + 120:
        if end > i_func + 1 and lines[end].startswith("def "):
            break
        end += 1

    print(f"=== keywords_for_phase 位于第 {i_func+1} 行 ===")
    print(f"=== 打印 {i_func+1} ~ {end} 行 ===\n")
    for j in range(i_func, end):
        print(f"{j+1:4d}| {lines[j]}")

    # 检查是否已包含 fields 逻辑
    func_body = "\n".join(lines[i_func:end])
    print("\n=== 关键检查 ===")
    print(f"  是否包含 'fields': {'是' if 'fields' in func_body else '否'}")
    print(f"  是否包含 '内容词': {'是' if '内容词' in func_body else '否'}")
    print(f"  是否包含 '动作词': {'是' if '动作词' in func_body else '否'}")
    print(f"  是否包含 '去重': {'是' if '去重' in func_body or '_seen' in func_body else '否'}")
