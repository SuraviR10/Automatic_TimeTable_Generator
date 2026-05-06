@echo off
cls
echo ============================================================
echo MIT MYSORE TIMETABLE SYSTEM
echo ============================================================
echo.
echo Starting server...
echo.
cd /d "%~dp0"
py unified_server.py
pause
