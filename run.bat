@echo off
REM UPC Validator - Windows Run Script
REM This script automatically checks dependencies and runs the application

echo ===============================================
echo  UPC Validator - Real-Time Barcode Checker
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python detected!
python --version
echo.

REM Check if dependencies are installed
echo Checking dependencies...
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo.
    echo Some dependencies are missing.
    echo Installing required packages...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo All dependencies installed!
echo.
echo Starting UPC Validator...
echo ===============================================
echo.

REM Run the application
python upc_validator_app.py

REM If the app exits with an error
if errorlevel 1 (
    echo.
    echo ===============================================
    echo ERROR: Application exited with an error
    echo.
    echo Troubleshooting:
    echo 1. Make sure all files are in the same directory
    echo 2. Try reinstalling dependencies: pip install -r requirements.txt
    echo 3. Check the error message above
    echo.
    pause
)

exit /b 0