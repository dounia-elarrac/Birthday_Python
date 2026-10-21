@echo off
setlocal
cd /d "%~dp0"

rem Find Python even when the Windows Python launcher has not registered it.
if exist "%LocalAppData%\Programs\Python\Python315\python.exe" (
  "%LocalAppData%\Programs\Python\Python315\python.exe" "%~dp0dounia_binary.py"
  if errorlevel 1 pause
  exit /b
)
for %%P in ("%LocalAppData%\Programs\Python\Python*\python.exe" "C:\Program Files\Python*\python.exe" "C:\Python3*\python.exe") do (
  if exist "%%~fP" (
    "%%~fP" "%~dp0dounia_binary.py"
    if errorlevel 1 pause
    exit /b
  )
)

where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0dounia_binary.py"
  if not errorlevel 1 exit /b
)

echo Python 3 was not found. Install Python 3, then run this file again.
echo If Python is already installed, reinstall it with the Tcl/Tk option enabled.
pause
