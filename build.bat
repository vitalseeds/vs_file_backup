@echo off
setlocal

where uv >nul 2>&1
if errorlevel 1 (
    echo Error: uv is not installed or not on PATH.
    echo Install it from https://docs.astral.sh/uv/
    exit /b 1
)

set "VENV=%~dp0.build_venv"

echo Creating build environment...
uv venv "%VENV%"
uv pip install --python "%VENV%\Scripts\python.exe" pyinstaller platformdirs

echo Building executable...
"%VENV%\Scripts\pyinstaller.exe" --onefile --console --name vs_backup "%~dp0vs_file_backup.py"

if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo.
echo Build complete: dist\vs_backup.exe
