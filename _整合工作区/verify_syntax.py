import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
try:
    import orchestrator
    print("[OK] orchestrator.py 语法正确")
except SyntaxError as e:
    print(f"[FAIL] 语法错误：{e}")
