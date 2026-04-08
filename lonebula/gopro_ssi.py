import subprocess
import os
import time

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
        # SSIのメインスレッドをブロックしないよう、run()ではなくPopen()を使用
        subprocess.Popen([PYTHON_EXE, SCRIPT_PATH, action], env=clean_env)
    except Exception as e:
        print(f"Error {action} GoPro: {e}")

def connect(opts, vars):
    print(">>> [SSI] WARM-UP PHASE: Pipeline connected. Waiting 30 seconds...")
    # trigger_gopro("stream_start")
    vars['start_time'] = time.time()
    vars['has_started'] = False
    vars['state_val'] = 0.0  # ウォームアップ中は0を出力

def read(name, sout, reset, board, opts, vars):
    # 1. 状態の更新とトリガー発行
    if not vars['has_started']:
        elapsed = time.time() - vars['start_time']
        if elapsed >= 5.0:
            print("\n" + "="*60)
            print(">>> [SSI] 1 MINUTE ELAPSED: PRODUCTION START! Triggering GoPro...")
            trigger_gopro("start")       # GoProの録画を開始
            vars['has_started'] = True   # 無限ループを防止
            vars['state_val'] = 1.0      # 録画中は1を出力
            
    # 2. 【超重要】SSIのバッファ(sout)を必ず埋める
    for i in range(sout.num):
        sout[i, 0] = vars['state_val']

def disconnect(opts, vars):
    # SSI終了時に自動でGoProの録画とストリームを停止
    print(">>> [SSI] Stopping GoPro...")
    trigger_gopro("stop")
    trigger_gopro("stream_stop")