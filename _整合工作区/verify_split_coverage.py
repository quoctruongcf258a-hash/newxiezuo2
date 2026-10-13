import sys, importlib, json
from pathlib import Path
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import orchestrator
importlib.reload(orchestrator)

print("=" * 70)
print("覆盖度校验函数测试")
print("=" * 70)

# 1. 合法：4 卷连续覆盖 1-150
good = {"列表": [
    {"key": "卷1", "start": 1, "end": 30},
    {"key": "卷2", "start": 31, "end": 80},
    {"key": "卷3", "start": 81, "end": 120},
    {"key": "卷4", "start": 121, "end": 150},
]}
ok, msg = orchestrator._validate_split_coverage(good, expected_total=150)
print(f"\n[1] 完整 4 卷：{'✅' if ok else '❌'} {msg}")

# 2. 缺卷：只有 3 卷，缺 31-80
bad1 = {"列表": [
    {"key": "卷1", "start": 1, "end": 30},
    {"key": "卷2", "start": 81, "end": 120},
    {"key": "卷4", "start": 121, "end": 150},
]}
ok, msg = orchestrator._validate_split_coverage(bad1, expected_total=150)
print(f"\n[2] 缺 31-80：{'✅' if ok else '❌'} {msg}")

# 3. 重叠
bad2 = {"列表": [
    {"key": "卷1", "start": 1, "end": 50},
    {"key": "卷2", "start": 40, "end": 100},
]}
ok, msg = orchestrator._validate_split_coverage(bad2, expected_total=150)
print(f"\n[3] 重叠（50 vs 40）：{'✅' if ok else '❌'} {msg}")

# 4. 不从 1 开始
bad3 = {"列表": [
    {"key": "卷1", "start": 10, "end": 150},
]}
ok, msg = orchestrator._validate_split_coverage(bad3, expected_total=150)
print(f"\n[4] start=10（不是 1）：{'✅' if ok else '❌'} {msg}")

# 5. 末尾不够
bad4 = {"列表": [
    {"key": "卷1", "start": 1, "end": 100},
]}
ok, msg = orchestrator._validate_split_coverage(bad4, expected_total=150)
print(f"\n[5] end=100（不是 150）：{'✅' if ok else '❌'} {msg}")

print(f"\n[6] 总章节数读取：{orchestrator._get_expected_total_chapters()}")
