@echo off
REM UPC Validator - Installation Script for Windows
REM This script installs all required and optional dependencies

echo ===============================================
echo  UPC Validator - Installation Script
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
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo Python detected!
python --version
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Ask user which installation type
echo Please select installation type:
echo.
echo [1] MINIMAL - Just validation and barcode generation
echo [2] FULL    - All features including webcam scanner
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Installing minimal dependencies...
    pip install Pillow python-barcode
) else if "%choice%"=="2" (
    echo.
    echo Installing all dependencies...
    pip install -r requirements.txt
) else (
    echo.
    echo Invalid choice. Installing minimal dependencies...
    pip install Pillow python-barcode
)

echo.
echo ===============================================
echo Installation complete!
echo ===============================================
echo.
echo To run the application, use:
echo    python upc_validator_app.py
echo.
echo Or simply double-click: run.bat
echo.
echo To test the installation:
echo    python test_upc_validator.py
echo.
pause