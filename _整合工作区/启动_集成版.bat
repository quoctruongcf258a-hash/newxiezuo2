@echo off
chcp 65001 >nul
rem 启动_集成版.bat —— 启动《赛马23环整合》集成版（SIM 模式）
rem 仅操作 F:\赛马23环整合工作室 内文件，原盘不动。
setlocal
set "PY=C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
cd /d "%~dp0"
if not exist "%PY%" set "PY=python"
"%PY%" 启动_集成版.py
echo.
echo 按任意键退出...
pause >nul
endlocal
