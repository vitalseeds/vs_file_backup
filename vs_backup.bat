@echo off
where uv >nul 2>&1
if errorlevel 1 (
    echo Error: uv is not installed or not on PATH.
    echo Install it from https://docs.astral.sh/uv/
    exit /b 1
)
uv run "%~dp0vs_backup_file.py" %*
