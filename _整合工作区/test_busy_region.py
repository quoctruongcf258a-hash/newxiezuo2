import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import is_ai_busy_pixel, is_ai_busy, _region_stats

print("region 统计 (CodeBuddy)：")
stats = _region_stats(651, 976, 680, 1003, 2)
print(f"  蓝/白/深/灰/总 = {stats}")
print()
print(f"is_ai_busy_pixel('CodeBuddy') = {is_ai_busy_pixel('CodeBuddy')}")
print(f"is_ai_busy('CodeBuddy')       = {is_ai_busy('CodeBuddy')}")
print()
print(f"is_ai_busy_pixel('Doubao')    = {is_ai_busy_pixel('Doubao')}")
print(f"is_ai_busy('Doubao')          = {is_ai_busy('Doubao')}")
