from pathlib import Path

bat = Path(r"F:\赛马23环整合工作室\_整合工作区\STOP_停止.bat")
content = '''@echo off
echo 正在停止所有流水线进程...
taskkill /F /IM python.exe /T 2>nul
echo.
echo 已发送停止信号。检查是否还有残留：
tasklist | findstr python
pause
'''
bat.write_text(content, encoding="gbk")
print(f"已创建：{bat}")
