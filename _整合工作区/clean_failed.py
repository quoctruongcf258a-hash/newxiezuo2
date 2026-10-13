from pathlib import Path
import shutil

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")
for d in ["_failed", "02_写作/W0_细纲分析/versions", "02_写作/W0_细纲分析/reviews", "02_写作/W0_细纲分析/merged"]:
    p = proj_root / d
    if p.exists():
        shutil.rmtree(p)
        print(f"已清空：{d}")
print("清理完成")
