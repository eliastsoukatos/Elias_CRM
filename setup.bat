@echo off
REM Windows batch script for CRM setup

REM Debug mode - set to 0 to hide detailed output, 1 to show it
set DEBUG=0

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="--debug" set DEBUG=1
shift
goto :parse_args
:end_parse

REM Helper function to log messages only in debug mode
:log
if %DEBUG%==1 echo %~1
goto :eof

REM Create virtual environment if it does not exist
if not exist "venv" (
    call :log "Creating virtual environment..."
    python -m venv venv > nul 2>&1
)

REM Activate virtual environment
call :log "Activating virtual environment..."
call venv\Scripts\activate.bat

REM Install requirements if requirements.txt exists
if exist "requirements.txt" (
    call :log "Installing dependencies from requirements.txt..."
    if %DEBUG%==1 (
        pip install -r requirements.txt
    ) else (
        pip install -r requirements.txt > nul 2>&1
    )
)

REM Check if Chrome is installed (needed for Selenium)
call :log "Checking Chrome installation (needed for Company Prospector)..."

REM Windows Chrome check
if not exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    if not exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
        call :log "Google Chrome is required for the Company Prospector feature."
        call :log "You can install it from: https://www.google.com/chrome/"
        call :log "Continuing with installation..."
    ) else (
        call :log "Google Chrome is installed."
    )
) else (
    call :log "Google Chrome is installed."
)

REM Note about ChromeDriver
if %DEBUG%==1 (
    call :log "Note: ChromeDriver is needed to run the Company Prospector feature."
    call :log "Selenium will attempt to find ChromeDriver automatically."
    call :log "If you experience issues, you may need to install ChromeDriver manually:"
    call :log "  - Visit https://chromedriver.chromium.org/downloads"
    call :log "  - Download the version matching your Chrome browser"
    call :log "  - Add it to your system PATH"
)

REM Update requirements.txt
call :log "Updating requirements.txt..."
if %DEBUG%==1 (
    pip freeze > requirements.txt
) else (
    pip freeze > requirements.txt 2>nul
)

REM Run main.py
call :log "Running main.py..."
REM Set DEBUG environment variable so Python can access it
set CRM_DEBUG=%DEBUG%
python main.py

exit /b 0