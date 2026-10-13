import sys
from pathlib import Path

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")

try:
    import orchestrator
    print("=== 模块 import 成功 ===")
    print(f"  _do_produce_renwu: {'存在' if hasattr(orchestrator, '_do_produce_renwu') else '缺失'}")
    print(f"  do_produce:       {'存在' if hasattr(orchestrator, 'do_produce') else '缺失'}")
    print(f"  _split_renwu:     {'存在' if hasattr(orchestrator, '_split_renwu') else '缺失'}")

    # 检查 do_produce 源码里是否含人物设计拦截
    import inspect
    src = inspect.getsource(orchestrator.do_produce)
    print(f"  do_produce 含人物设计分支：{'是' if '_do_produce_renwu' in src else '否'}")

    src2 = inspect.getsource(orchestrator._do_produce_renwu)
    print(f"  _do_produce_renwu 行数：{len(src2.splitlines())}")
    print(f"  含 人物设计列表 读取：{'是' if '人物设计列表' in src2 else '否'}")
    print(f"  含 单独调用 run_task：{'是' if 'run_task' in src2 else '否'}")
except SyntaxError as e:
    print(f"[SYNTAX ERROR] {e}")
except Exception as e:
    print(f"[ERROR] {e}")
