@echo off

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

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo.
    echo %ESC%[91m[ERROR]%ESC%[0m Virtual environment not found at %ESC%[94m%VENV_DIR%%ESC%[0m.
    echo Please run %ESC%[94mSetup.bat%ESC%[0m first to set up the project.
    goto :error
)

set VIRTUAL_ENV=
call "%VENV_DIR%\Scripts\activate.bat"
if not defined VIRTUAL_ENV (
    echo.
    echo %ESC%[91m[ERROR]%ESC%[0m Failed to activate virtual environment.
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
    echo %ESC%[91m[ERROR]%ESC%[0m This virtual environment was built with Python %ESC%[93m%PY_VERSION%%ESC%[0m
    echo   but this version of the app requires Python %ESC%[93m%MIN_PY_MAJOR%.%MIN_PY_MINOR%%ESC%[0m or later.
    echo   Please delete the %ESC%[94m%VENV_DIR%%ESC%[0m folder and run %ESC%[94mSetup.bat%ESC%[0m again.
    echo   Update your system python installation if necessary.
    goto :error
)

echo %ESC%[92mOK%ESC%[0m

echo Starting application...
python JobAppTracker\main.py

:done
exit /b %errorlevel%

:error
pause
exit /b 1
