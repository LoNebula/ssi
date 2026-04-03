@echo off
echo Starting Multi-Environment SSI System...

:: 1. GoPro用スクリプトを Python 3.11 環境で起動 (別ウィンドウ)
start "GoPro Streamer (Python 3.11)" cmd /c "C:\Users\shogo\anaconda3\envs\gopro\python.exe C:\ssi\lonebula\sender_gopro.py"

:: 2. ウェアラブル用スクリプトを別の環境で起動 (例として Python 3.8)
:: start "Wearable Streamer" cmd /c "C:\Users\shogo\anaconda3\envs\wearable\python.exe C:\ssi\lonebula\sender_wearable.py"

:: サーバー群が立ち上がるのを2秒待つ
timeout /t 2

:: 3. SSIパイプラインを Python 3.10 環境で起動
call C:\Users\shogo\anaconda3\Scripts\activate.bat ssi310
..\bin\x64\vc140\xmlpipe.exe multimodal.pipeline

echo Cleaning up...
:: SSI終了時にバックグラウンドのPythonプロセスも強制終了
taskkill /IM python.exe /F