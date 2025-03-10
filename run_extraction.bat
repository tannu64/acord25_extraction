@echo off
echo ACORD 25 Checkbox Extraction Tool
echo ================================
echo.

REM Activate the virtual environment
call ..\myenv\Scripts\activate.bat

REM Check if an image path was provided
if "%~1"=="" (
    echo Usage: run_extraction.bat [path_to_acord25_image_or_pdf]
    echo.
    echo Example: run_extraction.bat data\sample_acord25.pdf
    exit /b 1
)

REM Run the extraction script
python scripts\acord25_extractor.py --input "%~1" --output "results\extraction_results.json"

echo.
echo Extraction complete! Results saved to results\extraction_results.json
echo. 