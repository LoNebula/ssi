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

def connect(opts, vars):
    print(">>> [SSI] Pipeline Connected: Requesting Live Stream...")
    # プレビュー映像の配信だけは先に開始させておく
    trigger_gopro("stream_start")
    
    vars['has_started'] = False
    vars['read_count'] = 0
    vars['dummy_val'] = 1.0

def read(name, sout, reset, board, opts, vars):
    # 【重要】SSI本体のデータ取得ループが回り始めたら録画を開始
    if not vars['has_started']:
        vars['read_count'] += 1
        # 最初の初期化アクセスを飛ばし、完全にパイプラインが動いた直後（約1秒後）にキックする
        if vars['read_count'] >= 2:
            print(">>> [SSI] Pipeline Running: Starting GoPro Record NOW...")
            threading.Thread(target=trigger_gopro, args=("start",)).start()
            vars['has_started'] = True

    if name == 'state':
        val = vars['dummy_val']
        for n in range(sout.num):
            sout[n] = val

def disconnect(opts, vars):
    print(">>> [SSI] Pipeline Disconnected: Stopping GoPro...")
    # 録画とストリームの両方を停止
    trigger_gopro("stop")
    trigger_gopro("stream_stop")