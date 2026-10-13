import sys
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator

print("=== SPLIT_PRODUCERS（生产者）===")
for k, v in orchestrator.SPLIT_PRODUCERS.items():
    print(f"  {k}: {v}")

print("\n=== SPLIT_SOURCES（消费者）===")
for k, v in orchestrator.SPLIT_SOURCES.items():
    print(f"  {k}: {v}")
