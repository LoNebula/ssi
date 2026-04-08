import subprocess
import os
import threading
import queue

PYTHON_EXE = r"C:\Users\shogo\anaconda3\envs\movella\python.exe"
SCRIPT_PATH = r"C:\ssi\lonebula\movella_worker.py"

def getOptions(opts, vars):
    pass

def getChannelNames(opts, vars):
    return { 'sensor' : 'Movella DOT 9-ch (Time, Quat, FreeAcc, Status)' }

def initChannel(name, channel, types, opts, vars):
    if name == 'sensor':
        channel.dim = 9
        channel.type = types.FLOAT
        channel.sr = 60.0

def enqueue_output(out, q):
    for line in iter(out.readline, b''):
        line_str = line.decode('utf-8', errors='ignore').strip()
        if not line_str: continue
        try:
            vals = [float(x) for x in line_str.split(',')]
            if len(vals) == 9: q.put(vals)
            else: print(f"[Movella Worker] {line_str}")
        except ValueError:
            print(f"[Movella Worker] {line_str}")
    out.close()

def connect(opts, vars):
    print(">>> [SSI] Starting Movella (Outputting 0s while scanning)...")
    clean_env = os.environ.copy()
    clean_env.pop("PYTHONHOME", None)
    clean_env.pop("PYTHONPATH", None)
    
    try:
        proc = subprocess.Popen(
            [PYTHON_EXE, "-u", SCRIPT_PATH],
            env=clean_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
    except Exception as e:
        print(f"[Movella Error] Failed to start subprocess: {e}")
        return False
        
    q = queue.Queue()
    t = threading.Thread(target=enqueue_output, args=(proc.stdout, q))
    t.daemon = True
    t.start()
    
    vars['proc'] = proc
    vars['queue'] = q
    vars['last_data'] = [0.0] * 9
    vars['is_ready'] = False
    return True

def read(name, sout, reset, board, opts, vars):
    q = vars['queue']
    last_data = vars['last_data']
    
    # キューから最新の1つだけを取る、あるいは一定数で切り上げる
    got_new = False
    max_pull = 10 # 1回の呼び出しで処理する最大フレーム数
    count = 0
    while not q.empty() and count < max_pull:
        try:
            last_data = q.get_nowait()
            got_new = True
            count += 1
        except queue.Empty: break
            
    if got_new and not vars['is_ready']:
        vars['is_ready'] = True
        print(">>> [SSI] Movella Connected! Real data is now flowing.")
        
    vars['last_data'] = last_data
    
    # sout.num (SSIが要求しているフレーム数) 分を埋める
    for i in range(sout.num):
        for d in range(9):
            sout[i, d] = last_data[d]

def disconnect(opts, vars):
    if 'proc' in vars: vars['proc'].terminate()