"""collab_exec.py — 程序二·协同写作 执行引擎（兼容薄封装）。

真实执行逻辑已沉淀到 auto_stage.py（显式接入 windows-use/mix_send.send）。
本文件仅 re-export 对外符号，供 collab_app.py / ui_main.py 沿用既有调用：
    run_stage / run_all / run_all_threaded / set_dry_run / stop / DRY_RUN

如需改动执行流程，请在 auto_stage.py 中修改。
"""
from auto_stage import (
    run_stage,
    run_all,
    run_all_threaded,
    run_next_item,
    set_dry_run,
    start_run,
    stop,
    pause,
    resume,
    DRY_RUN,
    _produce_path,
    _review_path,
    _adjust_path,
    _context_path,
)

# 保持模块级可读别名
__all__ = [
    "run_stage", "run_all", "run_all_threaded", "run_next_item",
    "set_dry_run", "start_run", "stop", "pause", "resume", "DRY_RUN",
    "_produce_path", "_review_path", "_adjust_path", "_context_path",
]

if __name__ == "__main__":
    # 直接运行等价于运行 auto_stage 自测
    import runpy
    runpy.run_module("auto_stage", run_name="__main__")
