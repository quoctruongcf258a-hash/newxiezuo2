import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
import inspect

print("=" * 70)
print("重试/重发逻辑检查")
print("=" * 70)

# 1. 全局参数
print(f"\n[1] 重试参数")
for name in ["RETRY_T_FIRST", "RETRY_T_BUSY_LOOP", "RETRY_T_RETRY", "RETRY_MAX_ATTEMPTS"]:
    print(f"  {name} = {getattr(orchestrator, name, '缺失')}")

# 2. _do_produce_batch 里的重试循环
print(f"\n[2] _do_produce_batch 的重试循环")
src = inspect.getsource(orchestrator._do_produce_batch)
has_for = "for attempt in range(RETRY_MAX_ATTEMPTS)" in src
has_send = "_send_batch_task" in src
has_verify = "_wait_ai_task_done" in src
has_retry_next = "for ai_idx, ai_key in enumerate(ai_order)" in src
print(f"  AI 遍历循环：{'✅' if has_retry_next else '❌'}")
print(f"  单 AI 重试循环（for attempt）：{'✅' if has_for else '❌'}")
print(f"  发送任务：{'✅' if has_send else '❌'}")
print(f"  等完成（_wait_ai_task_done）：{'✅' if has_verify else '❌'}")

# 3. 试跑时是否真触发了失败重试
print(f"\n[3] _run_task_stage 的重试循环")
src2 = inspect.getsource(orchestrator._run_task_stage)
has_for2 = "for attempt in range(RETRY_MAX_ATTEMPTS)" in src2
has_retry_next2 = "for ai_idx, ai_key in enumerate(ai_order)" in src2
print(f"  AI 遍历循环：{'✅' if has_retry_next2 else '❌'}")
print(f"  单 AI 重试循环：{'✅' if has_for2 else '❌'}")

# 4. _send_batch_task 发送失败时怎么处理
print(f"\n[4] _send_batch_task")
src3 = inspect.getsource(orchestrator._send_batch_task)
print(f"  含 send 调用：{'✅' if 'send(' in src3 else '❌'}")
print(f"  含失败判定（非 ✅ 开头）：{'✅' if 'startswith' in src3 else '❌'}")

# 5. 关键：do_produce 里会不会短路到 _do_produce_batch
print(f"\n[5] do_produce 是否走 _do_produce_batch")
src4 = inspect.getsource(orchestrator.do_produce)
print(f"  含 _do_produce_batch：{'✅' if '_do_produce_batch' in src4 else '❌'}")

# 6. run_mesh_phase 是否走 _run_batch_mesh
print(f"\n[6] run_mesh_phase 是否走 _run_batch_mesh")
src5 = inspect.getsource(orchestrator.run_mesh_phase)
print(f"  含 _run_batch_mesh：{'✅' if '_run_batch_mesh' in src5 else '❌'}")
print(f"  含 SPLIT_PRODUCERS 或单件模式：{'✅' if '单件' in src5 or 'SPLIT_PRODUCERS' in src5 else '❌'}")
