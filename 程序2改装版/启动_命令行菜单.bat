@echo off
cd /d "%~dp0"
title 32流程版 - Command Line Menu

set "VENV=%~dp0windows-use\.venv"
set "VPY=%VENV%\Scripts\python.exe"
set "SRC=LOCAL"
if not exist "%VPY%" goto C_ORIG
if not exist "%VENV%\Lib\site-packages\psutil" goto C_ORIG
goto C_MENU

:C_ORIG
set "VPY=C:\mai\multi-ai-pipeline_webtest\windows-use\.venv\Scripts\python.exe"
set "SRC=ORIG"

:C_MENU
if not exist "%VPY%" (
  echo [ERROR] No usable python runtime found.
  pause
  exit /b 1
)

cd /d "%~dp0windows-use\_scratch"

:MENU
cls
echo ============================================
echo   32流程版  /  37-ring engine
echo   (planning 23 + writing 4 + polish 1 + QC 9)
echo ============================================
echo   [1] 校验今日阵容
echo   [2] 跑 规划 - 试运行 dry-run
echo   [3] 跑 规划 - 正式运行
echo   [4] 赛马记分榜
echo   [5] 查看今日阵容
echo   [0] 退出
echo ============================================
echo.
set "C="
set /p C=选择: 

if "%C%"=="1" "%VPY%" orchestrator.py --check-session & goto DONE
if "%C%"=="2" "%VPY%" orchestrator.py --program 规划 --dry-run & goto DONE
if "%C%"=="3" "%VPY%" orchestrator.py --program 规划 & goto DONE
if "%C%"=="4" "%VPY%" orchestrator.py --board & goto DONE
if "%C%"=="5" "%VPY%" session.py show & goto DONE
if "%C%"=="0" goto EOF
echo 无效选择
pause
goto MENU

:DONE
echo.
echo 完成。
pause
goto MENU

:EOF
exit /b 0
