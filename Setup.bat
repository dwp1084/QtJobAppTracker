@echo off

set REQUIREMENTS=requirements.txt
set UI_DIR=JobAppTracker\QtGUI\ui

for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

set CONFIG_FILE=%~dp0project.env
if not exist "%CONFIG_FILE%" (
    echo %ESC%[91m[ERROR]%ESC%[0m Could not find "%CONFIG_FILE%".
    goto :error
)
for /f "usebackq eol=# tokens=1,2 delims==" %%a in ("%CONFIG_FILE%") do (
    set "%%a=%%b"
)

set /p "=Checking python installation... " <nul

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo %ESC%[91m[ERROR]%ESC%[0m Python was not found on PATH
    echo Please install Python %ESC%[93m%MIN_PY_MAJOR%.%MIN_PY_MINOR%%ESC%[0m or later from %ESC%[94mhttps://www.python.org/downloads/%ESC%[0m
    goto :error
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VERSION=%%v
for /f "tokens=1,2 delims=." %%a in ("%PY_VERSION%") do (
    set PY_MAJOR=%%a
    set PY_MINOR=%%b
)

set PY_OK=1
if %PY_MAJOR% LSS %MIN_PY_MAJOR% set PY_OK=0
if %PY_MAJOR%==%MIN_PY_MAJOR% if %PY_MINOR% LSS %MIN_PY_MINOR% set PY_OK=0

if %PY_OK%==0 (
    echo.
    echo %ESC%[91m[ERROR]%ESC%[0m Python %ESC%[93m%PY_VERSION%%ESC%[0m found, but %ESC%[93m%MIN_PY_MAJOR%.%MIN_PY_MINOR%%ESC%[0m is required.
    goto :error
)

echo %ESC%[92mOK%ESC%[0m

set /p "=Creating virtual environment... " <nul

if exist "%VENV_DIR%\Scripts\python.exe" (
    echo %ESC%[93mAlready exists. Skipping.%ESC%[0m
) else (
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo.
        echo %ESC%[91m[ERROR]%ESC%[0m Failed to create virtual environment.
        goto :error
    ) else (
        echo %ESC%[92mOK%ESC%[0m
    )
)

set /p "=Activating virtual environment... " <nul

set VIRTUAL_ENV=
call "%VENV_DIR%\Scripts\activate.bat"
if not defined VIRTUAL_ENV (
    echo.
    echo %ESC%[91m[ERROR]%ESC%[0m Failed to activate virtual environment.
    goto :error
)

echo %ESC%[92mOK%ESC%[0m

echo Installing requirements...

python -m pip install --upgrade pip
pip install -r "%REQUIREMENTS%"
if errorlevel 1 (
    echo %ESC%[91m[ERROR]%ESC%[0m Failed to install requirements.
    goto :error
)

set /p "=Compiling UI files... " <nul

for %%f in ("%UI_DIR%\*.ui") do (
    pyuic6 "%%f" -o "%UI_DIR%\ui_%%~nf.py"
    if errorlevel 1 (
        echo.
        echo %ESC%[91m[ERROR]%ESC%[0m Failed to compile "%%f".
        goto :error
    )
)

echo %ESC%[92mOK%ESC%[0m

:done
echo ==== %ESC%[92mSetup complete!%ESC%[0m ====
echo To run the app, just run %ESC%[94mStart.bat%ESC%[0m
pause
exit /b 0

:error
echo %ESC%[91mSetup failed. Exiting.%ESC%[0m
pause
exit /b 1
