@echo off
powershell -file "%~dp0create_junction.ps1" %*
set /a RC=%ERRORLEVEL%
exit /b %RC%
