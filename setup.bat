@echo off
setlocal EnableExtensions
set "PV_ROOT=%~dp0"
cd /d "%PV_ROOT%" || goto :folder_failed
set "PV_PYTHON=%PV_ROOT%.venv\Scripts\python.exe"
set "PV_LOCAL_PYTHON=%PV_ROOT%.python\cpython-3.12.15-windows-x86_64-none\python.exe"
set "PV_LOCAL_UV=%PV_ROOT%.tools\uv.exe"
set "PV_ROOT=%CD%\"
title PolyVoice Setup

rem Keep inherited Python settings from affecting interpreter discovery or venv startup.
set "PYTHONHOME="
set "PYTHONPATH="
set "PYTHONNOUSERSITE=1"
set "PYTHONUTF8=1"

echo [1/8] Checking Windows compatibility...
if /i not "%PROCESSOR_ARCHITECTURE%"=="AMD64" goto :unsupported_arch
ver | findstr /c:"10.0." >nul
if errorlevel 1 goto :unsupported_windows

if not exist "%PV_ROOT%.tmp" mkdir "%PV_ROOT%.tmp" >nul 2>nul
if not exist "%PV_ROOT%.tools" mkdir "%PV_ROOT%.tools" >nul 2>nul
if not exist "%PV_ROOT%models\hf-cache" mkdir "%PV_ROOT%models\hf-cache" >nul 2>nul
set "TEMP=%PV_ROOT%.tmp"
set "TMP=%PV_ROOT%.tmp"
set "PIP_CACHE_DIR=%PV_ROOT%.pip-cache"
set "UV_CACHE_DIR=%PV_ROOT%.uv-cache"
set "UV_PYTHON_INSTALL_DIR=%PV_ROOT%.python"
set "HF_HOME=%PV_ROOT%models\hf-cache"
set "HF_HUB_CACHE=%PV_ROOT%models\hf-cache\hub"

if exist "%PV_PYTHON%" goto :check_existing_env

echo [2/8] Looking for a usable 64-bit Python 3.12...
where py >nul 2>nul
if not errorlevel 1 (
  py -3.12 -c "import encodings,platform,sys,venv; raise SystemExit(sys.version_info[:2] != (3,12) or platform.architecture()[0] != '64bit')" >nul 2>nul
  if not errorlevel 1 goto :use_launcher_python
)

where python >nul 2>nul
if not errorlevel 1 (
  python -c "import encodings,platform,sys,venv; raise SystemExit(sys.version_info[:2] != (3,12) or platform.architecture()[0] != '64bit')" >nul 2>nul
  if not errorlevel 1 goto :use_path_python
)

echo No suitable Python 3.12 was found. Preparing an isolated project-local Python runtime...
if exist "%PV_LOCAL_PYTHON%" goto :use_local_python
if exist "%PV_LOCAL_UV%" goto :bootstrap_python
where uv >nul 2>nul
if not errorlevel 1 goto :use_path_uv

echo Downloading the pinned, checksum-verified uv helper (approximately 15 MB)...
powershell.exe -NoLogo -NoProfile -NonInteractive -Command "$ErrorActionPreference='Stop'; $root=(Get-Location).Path; $tmp=Join-Path $root '.tmp'; $tools=Join-Path $root '.tools'; $zip=Join-Path $tmp 'uv-x64.zip'; $extract=Join-Path $tmp 'uv-x64'; Invoke-WebRequest -Uri 'https://github.com/astral-sh/uv/releases/download/0.13.3/uv-x86_64-pc-windows-msvc.zip' -OutFile $zip; $actual=(Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLower(); if($actual -ne 'bb701bd35b586c45966654ea2703c9bd116a6a4fc0a8ca755bd644c2c41c5ebe'){ throw 'uv SHA-256 verification failed.' }; Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force; $uv=Get-ChildItem -LiteralPath $extract -Filter 'uv.exe' -File -Recurse | Select-Object -First 1; if(-not $uv){ throw 'uv.exe was not found in the verified archive.' }; Copy-Item -LiteralPath $uv.FullName -Destination (Join-Path $tools 'uv.exe') -Force; Remove-Item -LiteralPath $zip,$extract -Recurse -Force"
if errorlevel 1 goto :uv_download_failed
goto :bootstrap_python

:use_path_uv
set "PV_UV=uv"
goto :bootstrap_python

:bootstrap_python
if not defined PV_UV set "PV_UV=%PV_LOCAL_UV%"
echo [3/8] Installing Python 3.12.15 inside the project (approximately 21 MB)...
"%PV_UV%" python install 3.12.15 --install-dir "%PV_ROOT%.python" --no-bin --no-registry
if errorlevel 1 goto :python_install_failed
if not exist "%PV_LOCAL_PYTHON%" goto :python_install_failed
set "PV_BASE_PYTHON=%PV_LOCAL_PYTHON%"
goto :validate_base_python

:use_launcher_python
echo Found Python through the Python Launcher.
echo [3/8] Checking standard library, memory guidance, and project disk space...
py -3.12 "%PV_ROOT%scripts\environment_check.py" --project-root "%PV_ROOT%." --preflight
if errorlevel 1 goto :preflight_failed
echo Creating the project virtual environment...
py -3.12 -m venv "%PV_ROOT%.venv"
if errorlevel 1 goto :venv_failed
goto :environment_ready

:use_path_python
echo Found Python 3.12 on PATH.
echo [3/8] Checking standard library, memory guidance, and project disk space...
python "%PV_ROOT%scripts\environment_check.py" --project-root "%PV_ROOT%." --preflight
if errorlevel 1 goto :preflight_failed
echo Creating the project virtual environment...
python -m venv "%PV_ROOT%.venv"
if errorlevel 1 goto :venv_failed
goto :environment_ready

:use_local_python
set "PV_BASE_PYTHON=%PV_LOCAL_PYTHON%"

:validate_base_python
"%PV_BASE_PYTHON%" "%PV_ROOT%scripts\environment_check.py" --project-root "%PV_ROOT%." --preflight
if errorlevel 1 goto :preflight_failed
echo Creating the project virtual environment...
"%PV_BASE_PYTHON%" -m venv "%PV_ROOT%.venv"
if errorlevel 1 goto :venv_failed

:environment_ready
if not exist "%PV_PYTHON%" goto :venv_failed
echo [4/8] Validating this project's Python environment...
"%PV_PYTHON%" "%PV_ROOT%scripts\environment_check.py" --project-root "%PV_ROOT%." --venv
if errorlevel 1 goto :python_version_failed
"%PV_PYTHON%" -m pip --version >nul 2>nul
if errorlevel 1 (
  echo Enabling pip inside the project virtual environment...
  "%PV_PYTHON%" -m ensurepip --upgrade
  if errorlevel 1 goto :pip_failed
)

echo [5/8] Checking pinned dependencies and local phonemizer runtime...
"%PV_PYTHON%" "%PV_ROOT%scripts\dependency_check.py"
if errorlevel 1 goto :install_dependencies
echo Existing dependencies are valid; skipping package reinstalls.
goto :models

:install_dependencies
echo Installing the CPU-only PyTorch runtime inside .venv...
echo Expect about 1.2-1.8 GB for package downloads and about 655 MB for German model assets.
echo Keep at least 5 GB free during setup. No administrator access is required.
"%PV_PYTHON%" -m pip install torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 goto :failed
echo Installing the pinned Kokoro, Misaki, Flask, phonemizer, and audio dependencies...
"%PV_PYTHON%" -m pip install -r "%PV_ROOT%requirements.txt"
if errorlevel 1 goto :failed
echo Checking the local English pronunciation model...
"%PV_PYTHON%" -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('en_core_web_sm') else 1)"
if errorlevel 1 (
  "%PV_PYTHON%" -m spacy download en_core_web_sm
  if errorlevel 1 goto :english_model_failed
)
echo Verifying that the English pronunciation model loads inside .venv...
"%PV_PYTHON%" -c "import spacy; spacy.load('en_core_web_sm')"
if errorlevel 1 goto :english_model_failed
echo Checking the installed Python packages, English model, and pinned source revisions...
"%PV_PYTHON%" "%PV_ROOT%scripts\dependency_check.py"
if errorlevel 1 goto :dependencies_failed

:models
echo [6/8] Preparing Kokoro weights and advertised voice packs...
"%PV_PYTHON%" "%PV_ROOT%scripts\cache_models.py"
if errorlevel 1 goto :models_failed
echo Preparing and verifying Kikiri German Martin...
"%PV_PYTHON%" "%PV_ROOT%scripts\cache_german_model.py"
if errorlevel 1 goto :models_failed
echo Preparing and verifying Kikiri German Victoria...
"%PV_PYTHON%" "%PV_ROOT%scripts\cache_german_victoria.py"
if errorlevel 1 goto :models_failed

echo [7/8] Running real local CPU speech and voice-preview checks for all languages...
"%PV_PYTHON%" "%PV_ROOT%scripts\smoke_test.py"
if errorlevel 1 goto :functional_test_failed

echo [8/8] Installation verified.
echo PolyVoice setup completed. CPU TTS, local voices, and WAV previews passed the functional checks.
echo Use start.bat to launch PolyVoice.
exit /b 0

:folder_failed
echo Could not switch to the PolyVoice project folder.
goto :failed

:unsupported_arch
echo PolyVoice currently requires 64-bit x64 Windows. ARM64 and 32-bit Windows are not supported.
goto :failed

:unsupported_windows
echo PolyVoice requires Windows 10 or Windows 11.
goto :failed

:uv_download_failed
echo The pinned uv helper could not be downloaded or its checksum did not match.
echo Check internet access. No unverified executable was run.
goto :failed

:python_install_failed
echo Could not prepare project-local Python 3.12.15. Check internet access and free disk space.
goto :failed

:preflight_failed
echo The Python, RAM, or disk-space preflight did not pass. Review the message above before retrying.
goto :failed

:venv_failed
echo Could not create or find the project's .venv. Check project-folder permissions and free disk space.
goto :failed

:python_version_failed
echo The project .venv is incomplete, moved, or not a 64-bit Python 3.12 environment.
echo Setup will not delete it. Rename or remove only this project's .venv, then run setup.bat again.
goto :failed

:pip_failed
echo pip could not be enabled inside the project .venv.
goto :failed

:dependencies_failed
echo Required packages, pinned source revisions, or local eSpeak NG files are missing.
echo Setup cannot report success until dependency verification passes.
goto :failed

:english_model_failed
echo The English pronunciation model en_core_web_sm could not be installed or loaded in .venv.
echo Check internet access, then run setup.bat again. The model is required for English speech.
goto :failed

:models_failed
echo A model or voice pack could not be prepared or verified. Check internet access and free disk space.
goto :failed

:functional_test_failed
echo The real local speech or preview test failed. Setup will not report success.
echo Review the error above, then rerun setup.bat after correcting the issue.
goto :failed

:failed
echo.
echo Setup failed. No system Python or Windows security settings were changed.
pause
exit /b 1
