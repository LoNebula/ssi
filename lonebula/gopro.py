import os
import sys

# --- DLL load failed 対策: Anaconda の Library\bin を直接登録 ---
conda_env = r'C:\Users\shogo\anaconda3\envs\ssi310'
dll_dir = os.path.join(conda_env, 'Library', 'bin')
if os.path.exists(dll_dir):
    os.add_dll_directory(dll_dir)
# -----------------------------------------------------------

import threading
import asyncio
import queue
import time
import numpy as np
from open_gopro import WirelessGoPro

# 以下、以前作成した関数群 (getChannelNames, initChannel, connect, read, disconnect)
def getChannelNames(opts, vars):
    return { 'gopro' : 'GoPro Sensor Data' }

def initChannel(name, channel, types, opts, vars):
    if name == 'gopro':
        channel.dim = 3
        channel.type = types.FLOAT
        channel.sr = 50.0

def connect(opts, vars):
    print("Connecting to GoPro...")
    vars['data_queue'] = queue.Queue()
    vars['stop_event'] = threading.Event()
    vars['thread'] = threading.Thread(target=_run_loop, args=(vars,), daemon=True)
    vars['thread'].start()
    vars['last_val'] = [0.0, 0.0, 0.0]
    return True

def _run_loop(vars):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def _task():
        try:
            async with WirelessGoPro() as gopro:
                print("GoPro: Connected!")
                while not vars['stop_event'].is_set():
                    # テスト用ダミーデータ
                    t = time.time()
                    vars['data_queue'].put([np.sin(t), np.cos(t), 0.0])
                    await asyncio.sleep(1.0 / 50.0)
        except Exception as e:
            print(f"GoPro Error: {e}")

    loop.run_until_complete(_task())

def read(name, sout, reset, board, opts, vars):
    for i in range(sout.num):
        try:
            val = vars['data_queue'].get_nowait()
            vars['last_val'] = val
        except:
            val = vars['last_val']
        
        if name == 'gopro':
            for d in range(3):
                sout[i, d] = float(val[d])

def disconnect(opts, vars):
    if 'stop_event' in vars:
        vars['stop_event'].set()