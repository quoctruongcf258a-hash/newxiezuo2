@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo  验证 rings_items.json 是否被 orchestrator 读入
echo ============================================================
echo.
python orchestrator.py --program 规划 --dry-run > _dry_out.txt 2>&1
echo --- 关键行 ---
findstr /C:"[rings]" /C:"环节数" /C:"跳过自动网格" /C:"参战" /C:"产出" /C:"盲审" /C:"拼接" _dry_out.txt
echo.
echo --- 完整输出已存到 _dry_out.txt ---
echo.
pause