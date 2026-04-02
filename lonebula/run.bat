@echo off
:: --- 1. shogoさんのAnaconda環境のパス ---
set CONDA_PATH=C:\Users\shogo\anaconda3
set ENV_PATH=%CONDA_PATH%\envs\ssi310

:: --- 2. 組み込みPythonが標準ライブラリを探せるように強制指定 ---
:: この PYTHONHOME がないと 'encodings' が見つかりません
set PYTHONHOME=%ENV_PATH%

:: --- 3. ライブラリの探索パスを連結 ---
set PYTHONPATH=C:\ssi\lonebula;%ENV_PATH%\Lib;%ENV_PATH%\Lib\site-packages;%ENV_PATH%\DLLs

:: --- 4. DLL（_ctypesなど）の依存解決のためにPATHを補強 ---
set PATH=C:\ssi\bin\x64\vc140;%ENV_PATH%;%ENV_PATH%\Library\bin;%ENV_PATH%\Scripts;%PATH%

echo --------------------------------------------------
echo [SSI] GoPro Sensor System (Full Path Mode)
echo PYTHONHOME: %PYTHONHOME%
echo --------------------------------------------------

:: --- 5. 実行 (カレントディレクトリを lonebula に固定) ---
cd /d C:\ssi\lonebula
C:\ssi\bin\x64\vc140\xmlpipe.exe gopro.pipeline

pause