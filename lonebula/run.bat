@echo off
set CONDA_BASE=C:\Users\shogo\anaconda3
set ENV_NAME=ssi310
set SSI_PATH=C:\ssi\bin\x64\vc140

:: 1. Conda環境を確実にアクティベート
call %CONDA_BASE%\Scripts\activate.bat %CONDA_BASE%\envs\%ENV_NAME%

:: 2. システムパスの再構築
set PATH=%SSI_PATH%;%CONDA_PREFIX%;%CONDA_PREFIX%\Library\bin;%CONDA_PREFIX%\Scripts;%PATH%

:: 3. ★修正箇所：組み込みPythonにConda環境の場所を教える
set PYTHONHOME=%CONDA_PREFIX%
set PYTHONPATH=C:\ssi\lonebula;%CONDA_PREFIX%\Lib;%CONDA_PREFIX%\DLLs

echo --------------------------------------------------
echo [SSI] Starting GoPro System with DLL Fix
echo ENV: %CONDA_PREFIX%
echo --------------------------------------------------

cd /d C:\ssi\lonebula
C:\ssi\bin\x64\vc140\xmlpipe.exe C:\ssi\lonebula\gopro.pipeline

pause