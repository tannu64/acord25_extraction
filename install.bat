@echo off
echo ACORD 25 Checkbox Extraction - Installation
echo =========================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in the PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    exit /b 1
)

REM Create a virtual environment
echo Creating virtual environment...
python -m venv myenv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment.
    exit /b 1
)

REM Activate the virtual environment
echo Activating virtual environment...
call myenv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment.
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    exit /b 1
)

echo.
echo Installation complete!
echo.
echo To use the ACORD 25 Checkbox Extraction tool:
echo 1. Place your ACORD 25 form images or PDFs in the 'data' directory
echo 2. Run 'run_extraction.bat data\your_form.pdf' to extract checkbox data
echo.
echo For more information, see the README.md file.
echo. 