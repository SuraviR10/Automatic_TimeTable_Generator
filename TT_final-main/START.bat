@echo off
echo ========================================
echo MIT Mysore Timetable System
echo Quick Start
echo ========================================
echo.
echo Checking Python...
py --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo.
echo Starting server...
echo.
echo Dashboard: http://localhost:5000/dashboard.htm
echo Generator: http://localhost:5000/timetable-new.htm
echo.
py unified_server.py
