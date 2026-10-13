@echo off
echo 正在停止所有流水线进程...
taskkill /F /IM python.exe /T 2>nul
echo.
echo 已发送停止信号。检查是否还有残留：
tasklist | findstr python
pause
