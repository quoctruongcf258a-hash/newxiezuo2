from pathlib import Path
import shutil

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
for d in ["01_规划/全书结构", "_failed"]:
    p = proj_root / d
    if p.exists():
        shutil.rmtree(p)
        print(f"已删：{d}")
