import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")

try:
    import orchestrator
    print("=== import 成功 ===")
    for fn in ["_read_expected_files", "_build_batch_prompt", "_write_failed_record",
               "_judge_task_status", "_send_batch_task", "_run_with_retry_fallback",
               "_do_produce_batch"]:
        ok = hasattr(orchestrator, fn)
        print(f"  {fn}: {'存在 [OK]' if ok else '缺失 [FAIL]'}")

    # 检查 do_produce 源码里是否用了 _do_produce_batch
    import inspect
    src = inspect.getsource(orchestrator.do_produce)
    print(f"\n  do_produce 用批量模式：{'是' if '_do_produce_batch' in src else '否'}")
except SyntaxError as e:
    print(f"[SYNTAX ERROR] {e}")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
