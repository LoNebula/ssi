import threading
import asyncio
import queue
import time
import numpy as np
from open_gopro import WirelessGoPro

# --------------------------------------------------
# グローバル変数 (SSIの各関数間で共有)
# --------------------------------------------------
_data_queue = queue.Queue()
_stop_event = threading.Event()

def getOptions(opts, vars):
    pass

def getChannelNames(opts, vars):
    # Movellaの例に倣い、チャンネル名と説明を定義
    return { 'gopro' : 'GoPro Sensor Data (Dummy Accel X, Y, Z)' }

def initChannel(name, channel, types, opts, vars):
    if name == 'gopro':
        channel.dim = 3        # 加速度 X, Y, Z の3次元
        channel.type = types.FLOAT
        channel.sr = 50.0      # サンプリングレート 50Hz
    else:
        print('unknown channel name')

def connect(opts, vars):
    print("--- GoPro Connecting ---")
    # 非同期ループを別スレッドで開始
    vars['thread'] = threading.Thread(target=_run_gopro_loop, daemon=True)
    vars['thread'].start()
    vars['last_val'] = [0.0, 0.0, 0.0]
    return True

def _run_gopro_loop():
    """GoPro SDKを制御するメインループ"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def _task():
        try:
            async with WirelessGoPro() as gopro:
                print("GoPro: Connection Established!")
                # ※ここで実際のSDKコマンド(加速度取得など)を記述
                while not _stop_event.is_set():
                    # テスト用：サイン波でダミーデータを生成
                    t = time.time()
                    fake_accel = [np.sin(t), np.cos(t), np.sin(t*0.5)]
                    _data_queue.put(fake_accel)
                    await asyncio.sleep(1.0 / 50.0) 
        except Exception as e:
            print(f"GoPro Thread Error: {e}")

    loop.run_until_complete(_task())

def read(name, sout, reset, board, opts, vars):
    """
    SSIから定期的に呼ばれる読み取り関数
    sout.num: 要求されているサンプル数
    """
    for i in range(sout.num):
        try:
            # キューからデータを取り出す
            val = _data_queue.get_nowait()
            vars['last_val'] = val
        except queue.Empty:
            # データがない場合は前回の値を保持
            val = vars['last_val']
        
        # movella.pyと同様に多次元配列として書き込み [サンプルIndex, 次元Index]
        if name == 'gopro':
            for d in range(3):
                sout[i, d] = float(val[d])

def disconnect(opts, vars):
    print("--- GoPro Disconnecting ---")
    _stop_event.set()
    if 'thread' in vars:
        vars['thread'].join(timeout=1.0)