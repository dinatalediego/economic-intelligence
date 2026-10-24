@echo off
setlocal

if "%~1"=="" (
    echo Usage: scripts\import_eip_exports.bat "C:\path\to\economic-intelligence-peru"
    exit /b 2
)

python "%~dp0import_eip_exports.py" --eip-root "%~1"
exit /b %ERRORLEVEL%
