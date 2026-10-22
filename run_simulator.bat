@echo off
title Resource Allocation Simulator - Banker's Algorithm
echo =====================================================================
echo   RESOURCE ALLOCATION SIMULATOR - BANKER'S ALGORITHM
echo   Deadlock Avoidance Interactive Simulator
echo =====================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Looking for Python in AppData...
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    ) else (
        echo [ERROR] Python not found in PATH or standard location.
        echo Please ensure Python 3.10+ is installed.
        pause
        exit /b 1
    )
) else (
    set "PYTHON_EXE=python"
)

echo [1/2] Verifying dependencies...
"%PYTHON_EXE%" -m pip install -r requirements.txt --quiet

echo [2/2] Launching Streamlit web application on port 8501...
echo The simulator will open in your default browser at http://localhost:8501
echo Press Ctrl+C in this terminal window to stop the server.
echo.
"%PYTHON_EXE%" -m streamlit run app.py
pause
