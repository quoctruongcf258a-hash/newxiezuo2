from pathlib import Path

# 找 P09 相关的 task 文件
task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
files = sorted(task_dir.glob("*.md"), key=lambda f: f.stat().st_mtime)

# 只看包含 "全书结构" 且是"产出"（不是盲审/拼接）的
p09_files = [f for f in files if "全书结构" in f.name]
print(f"共找到 {len(p09_files)} 个 P09 相关 task 文件")
print()

if p09_files:
    latest = p09_files[-1]
    print(f"📄 {latest.name}")
    print("=" * 70)
    txt = latest.read_text(encoding="utf-8")

    # 找"完整文件清单"节
    i = txt.find("需生成的完整文件清单")
    if i >= 0:
        # 打印到"## 输出位置"前
        j = txt.find("## 输出位置", i)
        if j < 0:
            j = i + 1000
        print(txt[i-50:j])

    print()
    print("=" * 70)
    print("输出位置章节：")
    print("=" * 70)
    k = txt.find("## 输出位置")
    if k >= 0:
        print(txt[k:k+300])

    print()
    print("=" * 70)
    print("完成判定章节：")
    print("=" * 70)
    m = txt.find("## 完成判定")
    if m >= 0:
        print(txt[m:m+400])
