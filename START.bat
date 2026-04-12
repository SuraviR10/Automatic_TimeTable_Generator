@echo off
title MIT Mysore Timetable System
color 0A
echo.
echo ============================================================
echo   MIT MYSORE TIMETABLE GENERATOR
echo   All Constraints Enforced
echo ============================================================
echo.
echo Checking Python...
py --version
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python not found!
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)
echo.
echo Starting Unified Timetable Engine...
echo.
echo Features:
echo  - 5 Hard Constraints Enforced
echo  - Lab Room Clash Prevention
echo  - Open Elective Same-Slot Enforcement
echo  - Global Faculty Conflict Detection
echo  - Retry Logic (5 attempts)
echo.
echo Server: http://localhost:5000
echo.
echo Press Ctrl+C to stop server
echo ============================================================
echo.
py unified_server.py
