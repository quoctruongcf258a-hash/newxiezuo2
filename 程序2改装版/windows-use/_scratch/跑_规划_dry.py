# 跑_规划_dry.py — 绕过 PowerShell 中文编码，直接调 orchestrator
import sys
import os

HERE = r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch"
os.chdir(HERE)
sys.path.insert(0, HERE)

# 输出写成 UTF-8 文件（记事本能正确显示，不会乱码）
out_path = os.path.join(HERE, "_dry_out_utf8.txt")
out = open(out_path, "w", encoding="utf-8")
sys.stdout = out
sys.stderr = out

# 直接设参数，不走命令行
sys.argv = ["orchestrator.py", "--program", "规划", "--dry-run"]

# 调 orchestrator
import orchestrator
try:
    orchestrator.main()
except SystemExit:
    pass
except Exception as e:
    print(f"\n[异常] {type(e).__name__}: {e}")
finally:
    out.close()

# 在真实 stdout 上提示
sys.__stdout__.write(f"\n✔ 已写入 {out_path}\n")
sys.__stdout__.write("  用记事本打开看：notepad " + out_path + "\n")