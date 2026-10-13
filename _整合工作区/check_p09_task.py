from pathlib import Path

# 找最新 P09 任务文件
task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
files = sorted(task_dir.glob("*全书结构*"), key=lambda f: f.stat().st_mtime)
if not files:
    print("❌ 找不到 P09 task 文件")
    raise SystemExit()

latest = files[-1]
print(f"📄 {latest.name}")
print("=" * 70)
txt = latest.read_text(encoding="utf-8", errors="ignore")

# 打印关键章节
for sec in ["需生成的完整文件清单", "## 输出格式要求", "## 输出位置", "## 完成判定"]:
    i = txt.find(sec)
    if i >= 0:
        # 找下一个 ## 或文件末尾
        j = txt.find("\n## ", i + 10)
        if j < 0:
            j = len(txt)
        print(f"\n{'='*70}")
        print(f"【{sec}】")
        print("=" * 70)
        print(txt[i:j][:1500])
