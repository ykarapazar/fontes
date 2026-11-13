@echo off
rem Double-click to add, change or remove the optional API keys (France, United States).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" keys
pause
