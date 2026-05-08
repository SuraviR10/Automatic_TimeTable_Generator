@echo off
echo ========================================
echo MIT Mysore Timetable System - Test Mode
echo ========================================
echo.

echo [1/4] Checking Python installation...
py --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)
echo.

echo [2/4] Starting server...
echo Server will start at: http://localhost:5000
echo.
echo IMPORTANT: Keep this window open!
echo.
echo To test:
echo 1. Subject Database: http://localhost:5000/subject.htm?dept=ISE
echo 2. Faculty Core: http://localhost:5000/faculty.htm?dept=ISE
echo 3. Test Dropdown: http://localhost:5000/test_dropdown.html
echo.
echo Press Ctrl+C to stop server
echo.
echo ========================================
echo.

py unified_server.py

pause
