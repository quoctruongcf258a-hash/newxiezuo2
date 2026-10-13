@echo off
chcp 65001 >nul
title 多 AI 快捷坐标录制与极速驱动工具

echo ========================================================
echo       多 AI 快捷坐标定位与驱动系统 (极速免 AI 大脑版)
echo ========================================================
echo.
echo [1] 录制/更新各个 AI 软件的按钮坐标 (运行 record_coords.py)
echo [2] 校验当前坐标配置 (查看 ai_coords.json)
echo [3] 退出
echo.
set /p opt=请选择操作编号 (1-3): 

if "%opt%"=="1" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0record_coords.py"
    pause
) else if "%opt%"=="2" (
    type "%~dp0ai_coords.json"
    pause
) else (
    exit
)
