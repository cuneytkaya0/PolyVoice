@echo off
setlocal
set "PV_ROOT=%~dp0"
cd /d "%PV_ROOT%" || goto :folder_failed
set "PYTHONHOME="
set "PYTHONPATH="
set "PYTHONNOUSERSITE=1"
set "PYTHONUTF8=1"
set "PV_PYTHON=%PV_ROOT%.venv\Scripts\python.exe"
set "PV_DIAG_ID=%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%"
set "PV_DIAG_DIR=%PV_ROOT%.tmp\diagnostics"
set "PV_DIAG_LOG=%PV_DIAG_DIR%\%PV_DIAG_ID%.log"
title PolyVoice

if not exist "%PV_DIAG_DIR%" mkdir "%PV_DIAG_DIR%" >nul 2>nul
for /f "skip=19 delims=" %%F in ('dir /b /a-d /o-d "%PV_DIAG_DIR%\*.log" 2^>nul') do del /f /q "%PV_DIAG_DIR%\%%F" >nul 2>nul
>"%PV_DIAG_LOG%" echo run_id=%PV_DIAG_ID%
>>"%PV_DIAG_LOG%" echo interpreter=%PV_PYTHON%
>>"%PV_DIAG_LOG%" echo started_local=%DATE% %TIME%
echo [PolyVoice diagnostics] run_id=%PV_DIAG_ID% log=%PV_DIAG_LOG%

if not exist "%PV_PYTHON%" goto :environment_missing

>>"%PV_DIAG_LOG%" echo stage=python-version started_local=%DATE% %TIME% command=environment-and-standard-library-check
"%PV_PYTHON%" "%PV_ROOT%scripts\environment_check.py" --project-root "%PV_ROOT%." --venv 2>>"%PV_DIAG_LOG%"
set "PV_STAGE_EXIT=%ERRORLEVEL%"
>>"%PV_DIAG_LOG%" echo stage=python-version exit_code=%PV_STAGE_EXIT% finished_local=%DATE% %TIME%
call :bound_diagnostics
echo [PolyVoice diagnostics] stage=python-version exit_code=%PV_STAGE_EXIT%
if not "%PV_STAGE_EXIT%"=="0" goto :environment_invalid

>>"%PV_DIAG_LOG%" echo stage=dependency-check started_local=%DATE% %TIME% command=pinned-dependency-and-local-espeak-check
"%PV_PYTHON%" "%PV_ROOT%scripts\dependency_check.py" 2>>"%PV_DIAG_LOG%"
set "PV_STAGE_EXIT=%ERRORLEVEL%"
>>"%PV_DIAG_LOG%" echo stage=dependency-check exit_code=%PV_STAGE_EXIT% finished_local=%DATE% %TIME%
call :bound_diagnostics
echo [PolyVoice diagnostics] stage=dependency-check exit_code=%PV_STAGE_EXIT%
if not "%PV_STAGE_EXIT%"=="0" goto :dependencies_missing

if not exist "%PV_ROOT%.tmp" mkdir "%PV_ROOT%.tmp"
if not exist "%PV_ROOT%models\hf-cache" mkdir "%PV_ROOT%models\hf-cache"
set "TEMP=%PV_ROOT%.tmp"
set "TMP=%PV_ROOT%.tmp"
set "HF_HOME=%PV_ROOT%models\hf-cache"
set "HF_HUB_CACHE=%PV_ROOT%models\hf-cache\hub"
set "TEMP=%PV_ROOT%.tmp"
set "TMP=%PV_ROOT%.tmp"

>>"%PV_DIAG_LOG%" echo stage=application started_local=%DATE% %TIME% command=python-run.py
"%PV_PYTHON%" "%PV_ROOT%run.py" 2>>"%PV_DIAG_LOG%"
set "PV_STAGE_EXIT=%ERRORLEVEL%"
>>"%PV_DIAG_LOG%" echo stage=application exit_code=%PV_STAGE_EXIT% finished_local=%DATE% %TIME%
call :bound_diagnostics
echo [PolyVoice diagnostics] stage=application exit_code=%PV_STAGE_EXIT%
if "%PV_STAGE_EXIT%"=="-1073741510" goto :normal_shutdown
if "%PV_STAGE_EXIT%"=="3221225786" goto :normal_shutdown
if not "%PV_STAGE_EXIT%"=="0" goto :runtime_failed
exit /b 0

:normal_shutdown
echo PolyVoice stopped by the user.
exit /b 0

:bound_diagnostics
powershell.exe -NoLogo -NoProfile -Command "$p='%PV_DIAG_LOG%'; $limit=262144; $marker='[earlier diagnostic output truncated]'+[Environment]::NewLine; if (Test-Path -LiteralPath $p) { $b=[IO.File]::ReadAllBytes($p); if ($b.Length -gt $limit) { $keep=$limit-[Text.Encoding]::UTF8.GetByteCount($marker); $i=$b.Length-$keep; $tail=[Text.Encoding]::UTF8.GetString($b,$i,$keep); [IO.File]::WriteAllText($p,($marker+$tail),(New-Object Text.UTF8Encoding($false))) } }" >nul 2>nul
exit /b 0

:folder_failed
echo Could not switch to the PolyVoice project folder.
goto :error_pause

:environment_missing
echo PolyVoice's project virtual environment was not found.
echo Run setup.bat from the PolyVoice folder, wait for it to complete, then run start.bat again.
echo Diagnostic log: %PV_DIAG_LOG%
type "%PV_DIAG_LOG%" 2>nul
goto :error_pause

:environment_invalid
echo The .venv Python is not Python 3.12 or does not belong to this PolyVoice folder.
echo Run setup.bat again. If it reports an invalid environment, remove only this project's .venv and retry.
echo Diagnostic log: %PV_DIAG_LOG%
type "%PV_DIAG_LOG%" 2>nul
goto :error_pause

:dependencies_missing
echo The project .venv is incomplete. One or more required packages are missing.
echo Run setup.bat from the PolyVoice folder, wait for successful dependency verification, then try again.
echo Diagnostic log: %PV_DIAG_LOG%
type "%PV_DIAG_LOG%" 2>nul
goto :error_pause

:runtime_failed
echo.
echo PolyVoice exited with an error. Run setup.bat to repair missing dependencies or models, then retry.
echo Diagnostic log: %PV_DIAG_LOG%
type "%PV_DIAG_LOG%" 2>nul
goto :error_pause

:error_pause
echo.
pause
exit /b 1
