import subprocess
import os
import threading

PYTHON_EXE = r"C:\Users\shogo\anaconda3\envs\gopro\python.exe"
SCRIPT_PATH = r"C:\ssi\lonebula\gopro_action.py"

def getOptions(opts, vars):
    pass

def getChannelNames(opts, vars):
    return { 'state' : 'GoPro connection status' }

def initChannel(name, channel, types, opts, vars):
    if name == 'state':
        channel.dim = 1
        channel.type = types.FLOAT
        channel.sr = 1.0 
    else:
        print('unknown channel name')

def trigger_gopro(action):
    clean_env = os.environ.copy()
    clean_env.pop("PYTHONHOME", None)
    clean_env.pop("PYTHONPATH", None)
    
    try:
        subprocess.run([PYTHON_EXE, SCRIPT_PATH, action], env=clean_env)
    except Exception as e:
        print(f"Error {action} GoPro: {e}")

def delayed_start():
    print(">>> [SSI] Pipeline Streaming: Starting GoPro Record NOW...")
    trigger_gopro("start")

def connect(opts, vars):
    print(">>> [SSI] Pipeline Connected: Requesting Live Stream...")
    # SSI起動と同時に、まずプレビュー映像の配信を開始させる
    trigger_gopro("stream_start")
    
    # 3秒カウントダウン後に録画を開始するタイマー
    timer = threading.Timer(3.0, delayed_start)
    timer.start()
    
    vars['dummy_val'] = 1.0

def read(name, sout, reset, board, opts, vars):
    if name == 'state':
        val = vars['dummy_val']
        for n in range(sout.num):
            sout[n] = val

def disconnect(opts, vars):
    print(">>> [SSI] Pipeline Disconnected: Stopping GoPro...")
    # 録画とストリームの両方を停止
    trigger_gopro("stop")
    trigger_gopro("stream_stop")