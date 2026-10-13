@echo off
cd /d "%~dp0"
title 32流程版 - Roster Console (23 rings)

rem 登记台用 tkinter；实测 venv 的 python 不带 tkinter，故优先系统 Python314
set "VPY=C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe"
if not exist "%VPY%" set "VPY=%~dp0windows-use\.venv\Scripts\python.exe"
if not exist "%VPY%" set "VPY=C:\mai\multi-ai-pipeline_webtest\windows-use\.venv\Scripts\python.exe"

if not exist "%VPY%" (
  echo.
  echo [ERROR] No usable python runtime found.
  echo.
  pause
  exit /b 1
)

echo ============================================
echo   32流程版  /  Roster Console
echo   Runtime : %VPY%
echo   Code    : %CD%
echo ============================================
echo.

"%VPY%" "windows-use\_scratch\gui_launcher.py"

echo.
echo ============ EXIT CODE = %errorlevel% ============
pause
