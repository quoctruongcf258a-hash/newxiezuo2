from pathlib import Path
import time

task_dir = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\_task_files")
files = sorted(task_dir.glob("*全书结构*"), key=lambda f: f.stat().st_mtime)

print(f"共 {len(files)} 个 P09 task 文件\n")
print("=" * 90)

for f in files[-10:]:
    t = time.strftime("%H:%M:%S", time.localtime(f.stat().st_mtime))
    txt = f.read_text(encoding="utf-8", errors="ignore")

    # 找输出位置
    i = txt.find("## 输出位置")
    out_loc = "?"
    if i >= 0:
        j = txt.find("\n", i + 20)
        line = txt[i:j] if j > 0 else txt[i:i+200]
        out_loc = line.replace("## 输出位置\n把最终结果保存到：", "").strip()[:120]

    # 判断类型：产出（versions）还是盲审（reviews）还是拼接（merged）
    kind = "?"
    if "/versions/" in out_loc or "\\versions\\" in out_loc:
        kind = "产出"
    elif "/reviews/" in out_loc or "\\reviews\\" in out_loc:
        kind = "盲审"
    elif "/merged/" in out_loc or "\\merged\\" in out_loc:
        kind = "拼接"

    print(f"  [{t}] {kind:4s} | {f.name[:70]}")
    print(f"           → {out_loc}")
