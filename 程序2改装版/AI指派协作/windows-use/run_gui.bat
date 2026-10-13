@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 多 AI 协作写作流水线 · 今日阵容登记台

REM ── 图形界面需要带 tkinter 的 Python；自动化层需要 .venv（装了 windows-use）。
REM    本脚本只负责把「能开窗」的解释器挑出来，不改变环境。

set "GUI_PY="

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import tkinter" >nul 2>&1
  if not errorlevel 1 set "GUI_PY=.venv\Scripts\python.exe"
)

if not defined GUI_PY if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
  "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" -c "import tkinter" >nul 2>&1
  if not errorlevel 1 set "GUI_PY=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
)

if not defined GUI_PY if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
  "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" -c "import tkinter" >nul 2>&1
  if not errorlevel 1 set "GUI_PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
)

if not defined GUI_PY (
  python -c "import tkinter" >nul 2>&1
  if not errorlevel 1 set "GUI_PY=python"
)

if not defined GUI_PY (
  echo.
  echo [ERROR] 找不到带 tkinter 的 Python，无法打开图形界面。
  echo         请安装官方 Python 并在安装时勾选 "tcl/tk and IDLE"。
  echo         或改用 run.bat 的命令行菜单。
  echo.
  pause
  exit /b 1
)

echo 使用解释器：%GUI_PY%
"%GUI_PY%" gui_launcher.py
pause
