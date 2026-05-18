@echo off
setlocal
title Whisper Flow uninstaller

echo Stopping any running Whisper Flow instances...
powershell -NoProfile -Command ^
    "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -match 'whisper_flow' -and $_.Name -match 'python' } | ForEach-Object { $_.Terminate() } | Out-Null"

echo Removing autostart shortcut...
powershell -NoProfile -Command ^
    "Remove-Item (Join-Path ([Environment]::GetFolderPath('Startup')) 'WhisperFlow.lnk') -Force -ErrorAction SilentlyContinue"

echo Removing lock file...
del /f /q "%~dp0.whisper_flow.lock" 2>nul

echo.
echo Whisper Flow has been stopped and removed from startup.
echo The source files in this folder are untouched - delete them manually if you want.
echo.
pause
