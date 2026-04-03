import subprocess
import os

# ※実際のパスに合わせてください
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
    """SSI(3.10)の環境変数がGoPro(3.11)に引き継がれるのを防ぐ"""
    clean_env = os.environ.copy()
    clean_env.pop("PYTHONHOME", None)
    clean_env.pop("PYTHONPATH", None)
    
    try:
        subprocess.Popen([PYTHON_EXE, SCRIPT_PATH, action], env=clean_env)
    except Exception as e:
        print(f"Error {action} GoPro: {e}")

def connect(opts, vars):
    print(">>> [SSI] Pipeline Connected: Starting GoPro...")
    trigger_gopro("start")
    vars['dummy_val'] = 1.0

def read(name, sout, reset, board, opts, vars):
    if name == 'state':
        val = vars['dummy_val']
        for n in range(sout.num):
            sout[n] = val

def disconnect(opts, vars):
    print(">>> [SSI] Pipeline Disconnected: Stopping GoPro...")
    trigger_gopro("stop")