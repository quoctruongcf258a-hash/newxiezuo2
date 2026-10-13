@echo off
cd /d "%~dp0"
title 32流程版 - Collab Writing Main UI

set "VENV=%~dp0windows-use\.venv"
set "VPY=%VENV%\Scripts\python.exe"
set "SRC=LOCAL"

rem 只有 python.exe 且 PySide6 齐全才算可用环境，否则回退原盘（避免用到复制一半的残缺 venv）
if not exist "%VPY%" goto USE_ORIG
if not exist "%VENV%\Lib\site-packages\PySide6" goto USE_ORIG
goto RUN

:USE_ORIG
set "VPY=C:\mai\multi-ai-pipeline_webtest\windows-use\.venv\Scripts\python.exe"
set "SRC=ORIG"

:RUN
if not exist "%VPY%" (
  echo.
  echo [ERROR] No usable python runtime found.
  echo   looked for: %VENV%\Scripts\python.exe
  echo   fallback  : C:\mai\multi-ai-pipeline_webtest\windows-use\.venv\Scripts\python.exe
  echo.
  pause
  exit /b 1
)

echo ============================================
echo   32流程版  /  Main UI
echo   Runtime : %VPY%
echo   Code    : %CD%
echo ============================================
echo.

"%VPY%" "app\collab_app.py"

echo.
echo ============ EXIT CODE = %errorlevel% ============
echo Non-zero means crashed; the Traceback above is the reason.
echo.
pause
