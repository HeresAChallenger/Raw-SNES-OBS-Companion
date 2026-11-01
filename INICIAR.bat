@echo off
setlocal EnableExtensions
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON=py -3"
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON=python"
  ) else (
    echo Python 3 nao encontrado. Instale o Python 3 e tente novamente.
    echo https://www.python.org/downloads/windows/
    pause
    exit /b 1
  )
)
:MENU
cls
echo ==============================================
echo    RAW-SNES OBS COMPANION - MENU
echo ==============================================
echo  1 - DEMONSTRACAO (sem login)
echo  2 - LIVE - 5 segundos (recomendado)
echo  3 - LIVE - 3 segundos
echo  4 - LIVE - 2 segundos (experimental)
echo  5 - LIVE - 10 segundos
echo  6 - LIVE - 15 segundos
echo  7 - Trocar usuario / Web API Key
echo  0 - Sair
echo ==============================================
set /p "CHOICE=Escolha: "
if "%CHOICE%"=="1" goto DEMO
if "%CHOICE%"=="2" goto LIVE5
if "%CHOICE%"=="3" goto LIVE3
if "%CHOICE%"=="4" goto LIVE2
if "%CHOICE%"=="5" goto LIVE10
if "%CHOICE%"=="6" goto LIVE15
if "%CHOICE%"=="7" goto RESET
if "%CHOICE%"=="0" exit /b 0
goto MENU
:DEMO
%PYTHON% rawsnes_obs.py --demo
pause
goto MENU
:LIVE5
%PYTHON% rawsnes_obs.py --interval 5
pause
goto MENU
:LIVE3
%PYTHON% rawsnes_obs.py --interval 3
pause
goto MENU
:LIVE2
%PYTHON% rawsnes_obs.py --interval 2
pause
goto MENU
:LIVE10
%PYTHON% rawsnes_obs.py --interval 10
pause
goto MENU
:LIVE15
%PYTHON% rawsnes_obs.py --interval 15
pause
goto MENU
:RESET
%PYTHON% rawsnes_obs.py --reset
pause
goto MENU
